from typing import List

import fastapi
from fastapi import UploadFile, Depends

from app.database import database
from app.database.schemas import UserSchema, UserInputSchema

from app.services.user_service import UserService
from app.types.UserInput import UserInput

router = fastapi.APIRouter()


@router.get("/all", response_model=List[UserSchema])
async def get_users(db=fastapi.Depends(database.get_db)):
    return await UserService.get_users(db)


@router.post("/create", response_model=UserSchema)
async def create_user(selfie_image: UploadFile, db=fastapi.Depends(database.get_db), user: UserInput = Depends()):
    return await UserService.create_user(db, UserInputSchema(**user.dict()), selfie_image)
