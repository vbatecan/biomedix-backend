import os

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

from ultralytics import YOLO

model = YOLO("models/detection.pt")
CONFIDENCE_THRESHOLD = 0.7


class ObjectDetectionService:
    @staticmethod
    async def detect_medicines(image):
        results = model(image, device="cpu")

        detected = []
        for result in results:
            for box in result.boxes:
                confidence = box.conf[0].item()
                if confidence > CONFIDENCE_THRESHOLD:
                    detected.append({
                        "label": model.names[int(box.cls[0].item())],
                        "confidence": confidence,
                        "bbox": box.xyxy[0].tolist()
                    })

        return detected
