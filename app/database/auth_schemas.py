from pydantic import BaseModel

from app.database.schemas import UserSchema


class LoginRequest(BaseModel):
    email: str
    password: str

class LoginSuccess(BaseModel):
    user: UserSchema
    ok: bool
    access_token: str
    token_type: str