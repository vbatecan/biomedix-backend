```
medicine_storage/
│── app/
│   │── __init__.py
│   │── main.py              # FastAPI app entrypoint
│   │
│   ├── core/
│   │   │── config.py        # settings (DB URL, paths, env vars)
│   │   │── security.py      # JWT tokens, password hashing
│   │
│   ├── database/
│   │   │── database.py      # engine, session, Base
│   │   │── models.py        # SQLAlchemy ORM models
│   │   │── schemas.py       # Pydantic schemas
│   │   │── crud.py          # database operations
│   │
│   ├── api/
│   │   │── __init__.py
│   │   │── routes_medicine.py   # medicine endpoints (CRUD, YOLO detection results)
│   │   │── routes_auth.py       # login, face recognition with DeepFace
│   │   │── routes_users.py      # staff management
│   │
│   ├── services/
│   │   │── face_recognition.py  # DeepFace integration
│   │   │── object_detection.py  # YOLO integration
│   │   │── inventory_service.py # stock/inventory logic
│   │
│   ├── utils/
│   │   │── logger.py        # logging configuration
│   │   │── helpers.py       # helper functions
│   │
│   ├── migrations/          # Alembic migration scripts
│
│── tests/                   # pytest test cases
│
│── requirements.txt
│── alembic.ini
│── .env                     # environment variables (DB URL, secrets, etc.)
│── README.md
```
🔹 Explanation of Key Parts
- main.py → boots the FastAPI app, includes routers.
- core/config.py → stores config (read from .env).
- database/ → models (ORM), schemas (Pydantic), crud (db logic).
- api/ → REST API endpoints grouped by feature (auth, medicine, users).
- services/ → ML logic (DeepFace + YOLO) separated from API logic.
- utils/ → helper modules (logging, etc.).
- migrations/ → Alembic migrations for DB schema.
- tests/ → unit + integration tests (FastAPI + DB + ML).