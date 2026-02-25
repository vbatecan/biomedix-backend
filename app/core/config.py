import os

import dotenv

dotenv.load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "default")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

DETECTION_CONFIDENCE = float(os.getenv("DETECTION_CONFIDENCE", 0.8))
CLASSIFICATION_CONFIDENCE = float(os.getenv("CLASSIFICATION_CONFIDENCE", 0.8))
FACE_RECOGNITION_CONF = float(os.getenv("FACE_RECOGNITION_CONFIDENCE", 0.75))

ENABLE_SERIAL_UNLOCK = os.getenv("ENABLE_SERIAL_UNLOCK", "true").lower() in {
    "1",
    "true",
    "yes",
    "on",
}
SERIAL_PORT = os.getenv("SERIAL_PORT", "")
SERIAL_BAUDRATE = int(os.getenv("SERIAL_BAUDRATE", os.getenv("SERIAL_BAUD_RATE", 9600)))
