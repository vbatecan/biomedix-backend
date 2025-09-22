import asyncio
import os
import asyncio

from datetime import datetime, timedelta
from ultralytics import YOLO
import numpy as np

model = YOLO("models/classification.pt")


class ClassificationService:
    def __init__(self):
        # Schedule periodic model checking
        self._last_model_mtime = os.path.getmtime('models/classification.pt')
        loop = asyncio.get_event_loop()
        loop.create_task(self._periodic_model_check())

    async def _periodic_model_check(self):
        while True:
            print("Checking for new model...")
            await self.check_new_model()
            await asyncio.sleep(5)  # Check every 60 seconds

    async def check_new_model(self):
        global model
        model_path = "models/classification.pt"

        # Check if model file exists
        if not os.path.exists(model_path):
            return

        # Get current model modification time
        current_mtime = os.path.getmtime(model_path)

        # Check if we have stored the previous modification time
        if not hasattr(self, '_last_model_mtime'):
            self._last_model_mtime = current_mtime
            return

        # If model file is newer, reload it
        if current_mtime > self._last_model_mtime:
            print("New model detected, reloading...")
            model = YOLO(model_path)
            self._last_model_mtime = current_mtime

    async def classify(self, cropped_image: np.ndarray):
        results = model(cropped_image, device="cpu")
        return results
