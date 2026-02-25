import logging
import os
import requests

import cv2
import fastapi
import numpy as np
from deepface import DeepFace
from pathlib import Path

from fastapi import UploadFile
from pandas.core.series import Series
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

import app.core.config as config
import app.core.security as security
import app.database.database as database
from app.database.schemas import RoleEnum, UserSchema
from app.services.authentication_history_service import AuthenticationHistoryService
from app.services.user_service import UserService

cabinet_url = "10.42.0.203"
TEST = False

router = fastapi.APIRouter()
logger = logging.getLogger(__name__)

df = DeepFace
FACE_RECOGNITION_CONF = config.FACE_RECOGNITION_CONF


def _extract_face_name(identity_path: str) -> str:
    """
    Extract folder name from DeepFace identity paths and tolerate Windows-style separators.
    """
    normalized_path = str(identity_path).replace("\\", "/").strip()
    parts = [part for part in normalized_path.split("/") if part]
    if len(parts) >= 2:
        return parts[-2].strip()
    return Path(normalized_path).stem.strip()


class Face(BaseModel):
    box: tuple[int, int, int, int]
    left_eye: tuple[int, int] | None
    right_eye: tuple[int, int] | None
    confidence: float


class FaceRecognitionResult(BaseModel):
    user: UserSchema
    face: Face
    identity: str
    confidence: float
    role: str
    token: str


# noinspection D
async def recognize_face(
    db: AsyncSession, image: np.ndarray, faces_detected: list[Face]
) -> list[FaceRecognitionResult]:
    face_identities = []
    for face in faces_detected:
        x, y, w, h = face.box
        # Add padding to the face crop to improve re-detection and alignment
        h_img, w_img, _ = image.shape
        padding = 0.20  # 20% padding
        
        pad_x = int(w * padding)
        pad_y = int(h * padding)
        
        x_new = max(0, x - pad_x)
        y_new = max(0, y - pad_y)
        w_new = min(w_img, x + w + pad_x) - x_new
        h_new = min(h_img, y + h + pad_y) - y_new
        
        face_img = image[y_new : y_new + h_new, x_new : x_new + w_new]
        try:
            results = df.find(
                img_path=face_img,
                db_path="./db",
                model_name="Facenet512",
                enforce_detection=False,
                silent=True,
                refresh_database=True,
                anti_spoofing=True,
                detector_backend="ssd",
                align=True,
            )
        except ValueError:
            logger.debug("No faces in the database to compare.")
            continue

        matched_user = False
        for result in results:
            if "identity" not in result:
                logger.debug("DeepFace result has no identity column: %s", result.columns)
                continue

            identity: Series = result["identity"]
            if "confidence" in result:
                confidence: Series = result["confidence"]
                # Confidence-based output: higher is better.
                combined = sorted(
                    list(zip(identity, confidence)),
                    key=lambda item: float(item[1]),
                    reverse=True,
                )
                score_mode = "confidence"
            elif "distance" in result:
                distance: Series = result["distance"]
                # Distance-based output: lower is better.
                combined = sorted(
                    list(zip(identity, distance)),
                    key=lambda item: float(item[1]),
                )
                score_mode = "distance"
            else:
                logger.debug("DeepFace result has no confidence/distance column: %s", result.columns)
                continue

            if not combined:
                logger.debug(
                    "No matches found for identities: %s",
                    identity.tolist() if hasattr(identity, "tolist") else identity,
                )
                continue

            for candidate_identity, candidate_score in combined:
                raw_score = float(candidate_score)

                if score_mode == "confidence":
                    # DeepFace confidence can be 0-1 or 0-100 depending on backend/version.
                    threshold = FACE_RECOGNITION_CONF
                    if raw_score > 1 and threshold <= 1:
                        threshold *= 100
                    elif raw_score <= 1 and threshold > 1:
                        threshold /= 100

                    if raw_score < threshold:
                        logger.debug(
                            "Skipping %s due to low confidence %.4f (< %.4f)",
                            candidate_identity,
                            raw_score,
                            threshold,
                        )
                        continue
                    reported_score = raw_score
                else:
                    if raw_score > FACE_RECOGNITION_CONF:
                        logger.debug(
                            "Skipping %s due to high distance %.4f (> %.4f)",
                            candidate_identity,
                            raw_score,
                            FACE_RECOGNITION_CONF,
                        )
                        continue
                    # Keep return field semantically as "confidence": 1-distance.
                    reported_score = max(0.0, 1.0 - raw_score)

                face_name = _extract_face_name(candidate_identity)
                if not face_name:
                    logger.debug("Could not extract face name from identity path: %s", candidate_identity)
                    continue

                logger.info("Recognized %s with %s score %.4f", face_name, score_mode, raw_score)
                user = await UserService.get_user_by_face_name(db, face_name)
                if not user:
                    logger.debug("No user matched face name '%s'", face_name)
                    continue

                token = await security.create_access_token(user.id, None)
                face_identities.append(
                    FaceRecognitionResult(
                        face=face,
                        identity=face_name,
                        confidence=reported_score,
                        role=user.role,
                        user=UserSchema.model_validate(user),
                        token=token,
                    )
                )

                # History write should not block successful recognition response.
                try:
                    await AuthenticationHistoryService.add_auth_access(db, user.id)
                except Exception as e:
                    logger.warning(
                        "Failed to write authentication history for user %s: %s",
                        user.id,
                        e,
                    )

                matched_user = True
                break

            if matched_user:
                break

    logger.info("Face identities: %s", face_identities)
    return face_identities


@router.post("/recognize")
async def face_recognition(image: UploadFile, db=fastapi.Depends(database.get_db)):
    try:
        content = await image.read()
        nparr = np.frombuffer(content, np.uint8)
        image_data = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image_data is None:
             raise fastapi.HTTPException(status_code=400, detail="Failed to decode image")
             
        logger.info("Received image: %s" % image.filename)
    except Exception as e:
        logger.error(f"Error processing image upload: {e}")
        raise fastapi.HTTPException(status_code=400, detail="Invalid image file")

    try:
        faces = df.extract_faces(
            image_data,
            enforce_detection=False,
            detector_backend="ssd",
            align=True,
            anti_spoofing=True,
        )
    except Exception as e:
        logger.error(f"Error extracting faces: {e}")
        # If face extraction fails, it might be due to no face or other issues.
        # DeepFace might raise ValueError or similar.
        return {"message": "No faces detected or error in processing"}

    if len(faces) <= 0:
        return {"message": "No faces detected"}

    faces_detected = []
    for face in faces:
        try:
            (x, y, w, h, left_eye, right_eye) = face["facial_area"].values()
            confidence = face["confidence"]
            is_real = face.get("is_real", None)
            antispoof_score = face.get("antispoof_score", None)

            if not is_real:
                logger.warning(
                    "Face at %s failed anti-spoofing check with score %s",
                    (x, y, w, h),
                    antispoof_score,
                )
                continue

            faces_detected.append(
                Face(
                    box=(x, y, w, h),
                    left_eye=left_eye,
                    right_eye=right_eye,
                    confidence=confidence,
                )
            )
        except Exception as e:
            logger.error(f"Error parsing face data: {e}")
            continue

    try:
        recognition_results = await recognize_face(db, image_data, faces_detected)
    except Exception as e:
        logger.error(f"Error in recognition logic: {e}", exc_info=True)
        raise fastapi.HTTPException(status_code=500, detail="Error during face recognition process")

    try:
        from app.services.serial_service import SerialService

        if len(recognition_results) > 0:
            SerialService.send_command("open")
        else:
            SerialService.send_command("close")
    except Exception as e:
        logger.error(f"Failed to trigger serial unlock: {e}")

    return recognition_results
