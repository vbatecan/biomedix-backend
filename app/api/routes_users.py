from typing import List

import fastapi
import os
from fastapi import UploadFile, Depends
from pydantic import BaseModel

from app.database import database
from app.database.models import User
from app.database.schemas import UserSchema, UserInputSchema

from app.services.user_service import UserService
from app.types.UserInput import UserInput

router = fastapi.APIRouter()


class ToggleUserActiveStatus(BaseModel):
    is_active: bool


@router.get("/all", response_model=List[UserSchema])
async def get_users(db=fastapi.Depends(database.get_db)):
    return await UserService.get_users(db)


@router.post("/create", response_model=UserSchema)
async def create_user(selfie_image: UploadFile, db=fastapi.Depends(database.get_db), user: UserInput = Depends()):
    return await UserService.create_user(db, UserInputSchema(**user.dict()), selfie_image)


@router.delete("/delete/{user_id}", response_model=UserSchema)
async def delete_user(user_id: int, db=fastapi.Depends(database.get_db)):
    try:
        user: User = await UserService.delete_user(db, user_id)

        if not user:
            raise ValueError("User not found.")

        face_folder_path = os.path.join("db", user.face_name)
        if os.path.exists(face_folder_path):
            for filename in os.listdir(face_folder_path):
                file_path = os.path.join(face_folder_path, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            os.rmdir(face_folder_path)

        return user
    except ValueError as e:
        raise fastapi.HTTPException(status_code=404, detail=str(e))


@router.patch("/toggle-active/{user_id}", response_model=UserSchema)
async def toggle_active_user(user_id: int, toggle: ToggleUserActiveStatus, db=fastapi.Depends(database.get_db)):
    try:
        user: User = await UserService.toggle_active_status(db, user_id, toggle.is_active)

        if not user:
            raise ValueError("User not found.")

        return user
    except ValueError as e:
        raise fastapi.HTTPException(status_code=404, detail=str(e))
