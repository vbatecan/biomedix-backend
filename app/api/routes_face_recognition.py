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
TEST = True

router = fastapi.APIRouter()
logger = logging.getLogger(__name__)

df = DeepFace
FACE_RECOGNITION_CONF = config.FACE_RECOGNITION_CONF


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
        face_img = image[y : y + h, x : x + w]
        try:
            results = df.find(
                img_path=face_img,
                db_path="./db",
                model_name="Facenet512",
                enforce_detection=False,
                silent=True,
                refresh_database=True,
                anti_spoofing=True,
                detector_backend="opencv",
                align=True,
            )
        except ValueError as e:  # No items found in the database
            logger.debug("No faces in the database to compare.")
            continue

        for result in results:
            identity: Series = result["identity"]
            confidence: Series = result["confidence"]
            combined = list(zip(identity, confidence))

            if not combined:
                print("No matches found")
                logger.debug(
                    "No matches found with identity: %s and confidence: %s",
                    identity,
                    confidence,
                )
                continue

            highest_confidence = max(combined, key=lambda x: x[1])
            print(f"High confidence match: {highest_confidence}")
            face_name = Path(highest_confidence[0]).parent.name
            logger.info(
                "Recognized %s with confidence %.2f", face_name, highest_confidence[1]
            )

            if highest_confidence[1] < FACE_RECOGNITION_CONF:  # Confidence threshold
                print("Was not able to go through the minimum confidence")
                continue
            else:
                print("Able to pass the confidence check.")

            user = await UserService.get_user_by_face_name(db, face_name)

            token = await security.create_access_token(user.id, None) if user else ""
            if user:
                record = await AuthenticationHistoryService.add_auth_access(db, user.id)

                if record:
                    face_identities.append(
                        FaceRecognitionResult(
                            face=face,
                            identity=face_name,
                            confidence=highest_confidence[1],
                            role=user.role,
                            user=UserSchema.model_validate(user),
                            token=token,
                        )
                    )
                else:
                    logger.debug(
                        "Failed to create authentication history record because of unknown error."
                    )
            else:
                logger.debug("No user was detected associated with this face name")
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
            detector_backend="opencv",
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

    if not TEST:
        try:
            requests.get(f"http://{cabinet_url}/unlock", timeout=1)
        except requests.RequestException as e:
            logger.error(f"Failed to unlock cabinet: {e}")
            # Do not fail the whole request just because cabinet unlock failed, but maybe warn?
            # Or maybe we should return a warning in the response.
            pass

    return recognition_results
