from datetime import timedelta, datetime, UTC
from passlib.context import CryptContext
from pydantic import BaseModel

import app.core.config as config
import jwt


class Token(BaseModel):
    sub: str
    exp: timedelta


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_access_token(user_id: int, expires_delta: timedelta | None) -> str:
    expires = datetime.now(UTC) + (
        expires_delta if expires_delta is not None else timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES))
    token = jwt.encode({"sub": str(user_id), "exp": expires}, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return token


async def verify_access_token(token: str) -> int:
    try:
        payload = jwt.decode(token, "your_secret_key", algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise ValueError("Invalid token")
        return int(user_id)
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.PyJWTError:
        raise ValueError("Invalid token")


async def decode_access_token(token: str) -> Token:
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.PyJWTError:
        raise ValueError("Invalid token")


async def hash_password(password: str) -> str:
    return pwd_context.hash(password)


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
