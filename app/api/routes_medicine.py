import logging
from typing import List
import uuid
import os

import cv2
import fastapi
import numpy as np
from fastapi import HTTPException, UploadFile, Depends
from ultralytics.engine.results import Probs

import app.database.database as db
from app.database.schemas import MedicineSchema
from app.services.classification import ClassificationService
from app.services.inventory_service import InventoryService
from app.services.object_detection import ObjectDetectionService
from app.types.MedicineInput import MedicineInput

router = fastapi.APIRouter()
logger = logging.getLogger(__name__)


# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
#
#
# async def get_current_user(request: fastapi.Request, token: str = fastapi.Depends(oauth2_scheme)):
#     try:
#         cookie_token = request.cookies.get("token")
#         if cookie_token:
#             token = cookie_token
#
#         payload = await security.decode_access_token(token)
#
#         if payload is None:
#             raise fastapi.HTTPException(status_code=401, detail="Invalid authentication credentials")
#         # You can add more checks here, like verifying user existence in the database or yung multi roles
#         return payload["sub"]
#     except ValueError as e:
#         print(f"Error decoding token: {e}")
#         raise fastapi.HTTPException(status_code=401, detail="Invalid authentication credentials")


# @router.get("/all", response_model=List[MedicineSchema])
# async def all(db=fastapi.Depends(db.get_db), current_user: str = fastapi.Depends(get_current_user)):
#     return await InventoryService.list_all(db)

@router.get("/all", response_model=List[MedicineSchema])
async def all(db=fastapi.Depends(db.get_db)):
    return await InventoryService.list_all(db)


@router.post("/add_stock")
async def add_stock(medicine_id: int, increment: int, user_id: int, db=fastapi.Depends(db.get_db)):
    return await InventoryService.add_stock(db, medicine_id, increment, user_id)


@router.get("/{medicine_id}", response_model=MedicineSchema)
async def get_medicine(medicine_id: int):
    return await InventoryService.get_medicine(medicine_id)


@router.get("/search/{name}")
async def search_medicine(name: str, db=fastapi.Depends(db.get_db)):
    medicines = await InventoryService.search_by_name(db, name)
    if not medicines:
        raise HTTPException(status_code=404, detail="No medicines found")
    return medicines


@router.post("/add")
async def add_medicine(
        thumbnail: UploadFile,
        training_files: list[UploadFile],
        db=fastapi.Depends(db.get_db),
        medicine_input: MedicineInput = Depends(),
):
    try:
        thumbnail_location = f"uploads/thumbnails/{medicine_input.name}.jpg"
        new_medicine = await InventoryService.add_medicine(db, medicine_input, thumbnail_location)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # save to uploads/thumbnails/thumbnail_filename.jpg
    if not thumbnail.filename:
        raise HTTPException(status_code=400, detail="No thumbnail filename provided")
    if not thumbnail.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid thumbnail file type. Please upload an image.")
    os.makedirs(os.path.dirname(thumbnail_location), exist_ok=True)
    with open(thumbnail_location, "wb") as f:
        f.write(await thumbnail.read())
    logger.info(f"Received thumbnail: {thumbnail.filename}")

    # save training files to uploads/training/medicine_name/filename.jpg
    training_location = f"uploads/training/{medicine_input.name}/"
    os.makedirs(training_location, exist_ok=True)
    if not training_files:
        raise HTTPException(status_code=400, detail="No training files provided")

    for training_file in training_files:
        if not training_file.filename:
            raise HTTPException(status_code=400, detail="One of the training files has no filename")
        if not training_file.content_type.startswith("image/"):
            raise HTTPException(status_code=400,
                                detail=f"Invalid training file type for {training_file.filename}. Please upload an image.")
        ext = os.path.splitext(training_file.filename)[1] or ".jpg"
        filename = f"{uuid.uuid4().hex}{ext}"
        training_file_location = os.path.join(training_location, filename)
        with open(training_file_location, "wb") as f:
            f.write(await training_file.read())
        logger.info(f"Received training file: {training_file.filename}")

    # TODO: Retrain the model with the new medicine
    return {"message": "Medicine added successfully", "medicine": new_medicine}


@router.put("/update/{medicine_id}")
async def update_medicine(medicine_id: int, name: str = None, description: str = None):
    pass


@router.delete("/delete/{medicine_id}")
async def delete_medicine(medicine_id: int):
    pass


@router.post("/recognize")
async def recognize_medicine(image: UploadFile):
    try:
        if not image.filename:
            raise HTTPException(status_code=400, detail="No filename provided")

        if not image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")

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
            classification = await ClassificationService.classify(cropped_image)

            result["classification"] = classification
            for classify in classification:
                probs: Probs = classify.probs
                detection_with_classification.append({
                    "detection": {
                        "label": class_id,
                        "confidence": confidence,
                        "bbox": {
                            "x": x1,
                            "y": y1,
                            "width": x2 - x1,
                            "height": y2 - y1
                        }
                    },
                    "classify": {
                        "product": classify.names[probs.top1],
                        "confidence": float(probs.top1conf)
                    }
                })

        logger.info(f"Received image: {image.filename}")

        return {"results": detection_with_classification}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
