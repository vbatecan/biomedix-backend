import os

import dotenv

dotenv.load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "your_default_secret_key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

DETECTION_CONFIDENCE = float(os.getenv("DETECTION_CONFIDENCE", 0.8))
CLASSIFICATION_CONFIDENCE = float(os.getenv("CLASSIFICATION_CONFIDENCE", 0.9))