import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from starlette.middleware.cors import CORSMiddleware

from app.api.routes_auth import router as auth_routes
from app.api.routes_users import router as users_routes
from app.api.routes_medicine import router as medicine_routes
from app.api.routes_face_recognition import router as face_recognition_routes
from app.scheduler.scheduler import start_scheduler, scheduler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:4200",
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    logger.info("Starting up...")
    start_scheduler()

    yield

    # Shutdown code
    scheduler.shutdown()
    logger.info("Shutting down...")


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes, prefix="/auth", tags=["auth"])
app.include_router(users_routes, prefix="/users", tags=["users"])
app.include_router(medicine_routes, prefix="/medicines", tags=["medicines"])
app.include_router(face_recognition_routes, prefix="/faces", tags=["faces"])


@app.get("/")
async def health_check():
    return {"status": "ok"}
