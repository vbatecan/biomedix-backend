from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    password: str

class LoginSuccess(BaseModel):
    ok: bool
    access_token: str
    token_type: str