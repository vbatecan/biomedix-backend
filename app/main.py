from fastapi import FastAPI, Depends
from starlette.middleware.cors import CORSMiddleware

from app.api.routes_auth import router as auth_routes
from app.api.routes_users import router as users_routes
from app.api.routes_medicine import router as medicine_routes
from app.api.routes_face_recognition import router as face_recognition_routes

app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:4200",
]

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