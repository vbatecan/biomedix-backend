import logging
import os
import uuid
from datetime import datetime, timedelta
from typing import List

import cv2
import fastapi
import numpy as np
from fastapi import HTTPException, UploadFile, Depends
from fastapi.security import OAuth2PasswordBearer
from ultralytics.engine.results import Probs

import app.database.database as db
from app.core import security
from app.database.schemas import MedicineSchema
from app.scheduler.scheduler import scheduler
from app.scheduler.tasks import retrain_classification_model
from app.services.classification import ClassificationService
from app.services.inventory_service import InventoryService
from app.services.object_detection import ObjectDetectionService
from app.types.MedicineInput import MedicineInput

router = fastapi.APIRouter()
logger = logging.getLogger(__name__)
cls_service = ClassificationService()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(request: fastapi.Request, token: str = fastapi.Depends(oauth2_scheme)):
    try:
        logger.info("Working")
        cookie_token = request.cookies.get("token")
        if cookie_token:
            token = cookie_token

        payload = await security.decode_access_token(token)

        if payload is None:
            raise fastapi.HTTPException(status_code=401, detail="Invalid authentication credentials")
        # You can add more checks here, like verifying user existence in the database or yung multi roles
        return payload["sub"]
    except ValueError as e:
        logger.error(f"Error decoding token: {e}")
        raise fastapi.HTTPException(status_code=401, detail="Invalid authentication credentials")





@router.get("/all", response_model=List[MedicineSchema])
async def all(db=fastapi.Depends(db.get_db)):
    return await InventoryService.list_all(db)


@router.post("/add_stock")
async def add_stock(
        medicine_name: str, quantity: int, db=fastapi.Depends(db.get_db), user=fastapi.Depends(get_current_user)
):
    user_id = int(user) if user and user.isdigit() else None
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid user ID")

    try:
        return await InventoryService.add_stock(db, medicine_name, quantity, user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/reduce_stock")
async def reduce_stock(
        medicine_name: str, quantity: int, db=fastapi.Depends(db.get_db), user=fastapi.Depends(get_current_user)
):
    user_id = int(user) if user and user.isdigit() else None
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid user ID")
    try:
        return await InventoryService.reduce_stock(db, medicine_name, quantity, user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{medicine_id}", response_model=MedicineSchema)
async def get_medicine(medicine_id: int, db=fastapi.Depends(db.get_db)):
    medicine = await InventoryService.get_medicine(db, medicine_id)
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    return medicine


@router.get("/search/{name}")
async def search_medicine(name: str, db=fastapi.Depends(db.get_db)):
    try:
        medicines = await InventoryService.search_by_name(db, name)
        if not medicines:
            raise HTTPException(status_code=404, detail="No medicines found")
        return medicines
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/add")
async def add_medicine(
        thumbnail: UploadFile,
        training_files: list[UploadFile],
        immediate_training: bool = False,
        # Development parameter: if True, starts training immediately with faster settings
        db=fastapi.Depends(db.get_db),
        medicine_input: MedicineInput = Depends(),
):
    """
    Add a new medicine to the system.

    Args:
        thumbnail: Medicine thumbnail image
        training_files: Training images for the classification model
        immediate_training: Development only - if True, starts training immediately with faster settings (10 epochs)
        medicine_input: Medicine details (name, description, etc.)

    Returns:
        Success message with medicine details and training information
    """
    try:
        thumbnail_location = f"uploads/thumbnails/{medicine_input.name}.jpg"
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # save to uploads/thumbnails/thumbnail_filename.jpg
    if not thumbnail.filename:
        raise HTTPException(status_code=400, detail="No thumbnail filename provided")
    if not thumbnail.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Invalid thumbnail file type. Please upload an image.",
        )
    os.makedirs(os.path.dirname(thumbnail_location), exist_ok=True)
    with open(thumbnail_location, "wb") as f:
        f.write(await thumbnail.read())
    logger.info(f"Received thumbnail: {thumbnail.filename}")

    # save training files to uploads/training/medicine_name/filename.jpg
    training_location = f"uploads/training/{medicine_input.name}/"
    os.makedirs(training_location, exist_ok=True)
    if not training_files:
        raise HTTPException(status_code=400, detail="No training files provided")

    try:
        for training_file in training_files:
            if not training_file.filename:
                raise HTTPException(
                    status_code=400, detail="One of the training files has no filename"
                )
            if not training_file.content_type.startswith("image/"):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid training file type for {training_file.filename}. Please upload an image.",
                )

            # Convert file to numpy array for detection
            image_data = cv2.imdecode(
                np.frombuffer(await training_file.read(), np.uint8), cv2.IMREAD_COLOR
            )
            result = await ObjectDetectionService.detect_medicines(image_data)

            # Crop the detected medicine from the image
            if not result:
                raise HTTPException(
                    status_code=400,
                    detail=f"No medicine detected in training image {training_file.filename}. Please upload a clear image of the medicine.",
                )
            x1, y1, x2, y2 = map(int, result[0]["bbox"])
            cropped_image = image_data[y1:y2, x1:x2]

            # Save cropped image
            ext = os.path.splitext(training_file.filename)[1] or ".jpg"
            filename = f"{uuid.uuid4().hex}{ext}"
            training_file_location = os.path.join(training_location, filename)
            cv2.imwrite(training_file_location, cropped_image)
            logger.info(f"Received and processed training file: {training_file.filename}")

    except cv2.error as e:
        logger.error(f"OpenCV error in add_medicine: {e}")
        raise HTTPException(status_code=400, detail="Error processing image. The file might be corrupted.")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in add_medicine: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred while adding the medicine.")

    try:
        new_medicine = await InventoryService.add_medicine(
            db, medicine_input, thumbnail_location
        )

        if not new_medicine:
            raise HTTPException(status_code=500, detail="Failed to add medicine to database")

        job_id = f"train_{medicine_input.name}"
        if immediate_training:
            scheduler.add_job(
                retrain_classification_model,
                "date",
                id=job_id,
                replace_existing=True,
            )
        else:
            scheduler.add_job(
                retrain_classification_model,
                "date",
                run_date=datetime.now() + timedelta(minutes=10),
                id=job_id,
                replace_existing=True,
            )
        return new_medicine
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error saving medicine to database: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to save medicine information.")




@router.delete("/delete/{medicine_id}", response_model=MedicineSchema)
async def delete_medicine(medicine_id: int, db=fastapi.Depends(db.get_db)):
    try:
        medicine: MedicineSchema = await InventoryService.delete_medicine(db, medicine_id)

        # Also delete associated training images
        training_dir = f"uploads/training/{medicine.name}/"

        if os.path.exists(training_dir):
            logger.debug("Removing training images at %s", training_dir)
            for root, dirs, files in os.walk(training_dir, topdown=False):
                for file in files:
                    os.remove(os.path.join(root, file))
                for dir in dirs:
                    os.rmdir(os.path.join(root, dir))
            os.rmdir(training_dir)

        # Remove thumbnail
        if medicine.image_path and os.path.exists(medicine.image_path):
            logger.debug("Removing thumbnail at %s", medicine.image_path)
            os.remove(medicine.image_path)

        return medicine
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/uploads/thumbnails/{filename}")
async def get_thumbnail(filename: str):
    file_path = os.path.join("uploads", "thumbnails", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Thumbnail not found")
    return fastapi.responses.FileResponse(file_path)


@router.post("/recognize")
async def recognize_medicine(image: UploadFile):
    try:
        if not image.filename:
            raise HTTPException(status_code=400, detail="No filename provided")

        if not image.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400, detail="Invalid file type. Please upload an image."
            )

        # Convert to numpy array
        image_data = cv2.imdecode(
            np.frombuffer(await image.read(), np.uint8), cv2.IMREAD_COLOR
        )

        results = await ObjectDetectionService.detect_medicines(image_data)

        detection_with_classification = []
        for result in results:
            class_id = result["label"]
            confidence = result["confidence"]
            bbox = result["bbox"]

            # Crop the detected medicine from the image
            x1, y1, x2, y2 = map(int, bbox)
            cropped_image = image_data[y1:y2, x1:x2]

            # Classify the cropped image
            classification = await cls_service.classify(cropped_image)

            result["classification"] = classification
            for classify in classification:
                probs: Probs = classify.probs
                detection_with_classification.append(
                    {
                        "detection": {
                            "label": class_id,
                            "confidence": confidence,
                            "bbox": {
                                "x": x1,
                                "y": y1,
                                "width": x2 - x1,
                                "height": y2 - y1,
                            },
                        },
                        "classify": {
                            "product": classify.names[probs.top1],
                            "confidence": float(probs.top1conf),
                        },
                    }
                )

        logger.info(f"Received image: {image.filename}")

        return {"results": detection_with_classification}
    except cv2.error as e:
        logger.error(f"OpenCV error in recognize_medicine: {e}")
        raise HTTPException(status_code=400, detail="Error processing image for recognition. The image might be corrupted.")
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in recognize_medicine: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred during medicine recognition.")
