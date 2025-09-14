import logging

import cv2
import fastapi
import numpy as np
import app.database.database as database
import app.core.security as security
from deepface import DeepFace
from fastapi import UploadFile
from pandas.core.series import Series
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.schemas import RoleEnum
from app.services.user_service import UserService

router = fastapi.APIRouter()
logger = logging.getLogger(__name__)

df = DeepFace


class Face(BaseModel):
    box: tuple[int, int, int, int]
    left_eye: tuple[int, int] | None
    right_eye: tuple[int, int] | None
    confidence: float


class FaceRecognitionResult(BaseModel):
    face: Face
    identity: str
    confidence: float
    role: RoleEnum
    token: str


async def recognize_face(db: AsyncSession, image: np.ndarray, faces_detected: list[Face]) -> list[
    FaceRecognitionResult]:
    # For each face detected, crop and recognize, use find() function and add to list of known faces
    face_identities = []
    for face in faces_detected:
        (x, y, w, h) = face.box
        face_img = image[y: y + h, x: x + w]
        results = df.find(
            img_path=face_img,
            db_path="./db",  # Update with your face database path
            model_name="VGG-Face",
            enforce_detection=False,
            silent=True,
            refresh_database=True
        )

        for result in results:
            identity: Series = result["identity"]
            confidence: Series = result["confidence"]
            combined = list(zip(identity, confidence))
            highest_confidence = max(combined, key=lambda x: x[1])
            face_name = highest_confidence[0].split("/")[-2].split(".")[0]
            logger.info(f"Recognized {face_name} with confidence {highest_confidence[1]}")

            # Get User by Face Name
            user = await UserService.get_user_by_face_name(db, face_name)
            # Generate token if user exists
            token = await security.create_access_token(user.id, None) if user else ""
            if user:
                face_identities.append(
                    FaceRecognitionResult(
                        face=face,
                        identity=highest_confidence[0].split("/")[-2].split(".")[0],
                        confidence=highest_confidence[1],
                        role=user.role,
                        token=token
                    )
                )

    return face_identities


@router.post("/recognize")
async def face_recognition(image: UploadFile, db=fastapi.Depends(database.get_db)):
    image_data = cv2.imdecode(
        np.frombuffer(await image.read(), np.uint8), cv2.IMREAD_COLOR
    )
    logger.info(f"Received image: {image}")
    faces = df.extract_faces(image_data, enforce_detection=False, detector_backend="opencv", align=False,
                             anti_spoofing=True)
    if len(faces) <= 0:
        return {"message": "No faces detected"}

    faces_detected = []
    for face in faces:
        (x, y, w, h, left_eye, right_eye) = face["facial_area"].values()
        confidence = face["confidence"]
        faces_detected.append(
            Face(
                box=(x, y, w, h),
                left_eye=left_eye,
                right_eye=right_eye,
                confidence=confidence,
            )
        )

    recognition_results = await recognize_face(db, image_data, faces_detected)
    logger.info("Returning recognition results", recognition_results)
    return recognition_results
