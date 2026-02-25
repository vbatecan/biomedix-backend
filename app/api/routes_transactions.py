import logging
from datetime import datetime
from typing import List

import fastapi
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer

from app.core import security
from app.database.database import get_db
from app.database.schemas import TransactionSchema
from app.services.transaction_service import TransactionService
from app.utils.datetimerange import DateTimeRange

router = APIRouter()
logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(request: fastapi.Request, token: str = fastapi.Depends(oauth2_scheme)):
    try:
        cookie_token = request.cookies.get("token")
        if cookie_token:
            token = cookie_token

        payload = await security.decode_access_token(token)

        if payload is None:
            raise fastapi.HTTPException(status_code=401, detail="Invalid authentication credentials")
        # can add more checks here, like verifying user existence in the database or yung multi roles
        return payload["sub"]
    except ValueError as e:
        print(f"Error decoding token: {e}")
        raise fastapi.HTTPException(status_code=401, detail="Invalid authentication credentials")


@router.get("/all", response_model=List[TransactionSchema])
async def all(page: int = 0, size: int = 10, db=Depends(get_db)):
    return await TransactionService.all(db, page, size)


@router.get("/user/all")
async def get_user_transactions(start_datetime: datetime, end_datetime: datetime,
                                user_id: int = Depends(get_current_user), db=Depends(get_db)):
    date_range = DateTimeRange(start_datetime, end_datetime)
    result = await TransactionService.get_user_transactions(db, user_id, date_range, page=1, size=10)
    return result
