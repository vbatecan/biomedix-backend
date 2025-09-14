from ultralytics import YOLO
import numpy as np

model = YOLO("models/classification.pt")


class ClassificationService:
    @staticmethod
    async def classify(cropped_image: np.ndarray):
        results = model(cropped_image, device="cpu")
        return results
