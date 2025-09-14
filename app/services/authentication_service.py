from sqlalchemy import sql
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.auth_schemas import LoginSuccess
from app.database.models import User
import app.core.security as security
from app.database.schemas import MessageResponse


class AuthenticationService:

    @staticmethod
    async def authenticate(db: AsyncSession, email: str, password: str):
        if email == "" or password == "":
            return MessageResponse(ok=False, message="Email and password are required")

        user = await db.execute(sql.select(User).where(User.email == email))
        result = user.scalar_one_or_none()

        if result is None:
            return MessageResponse(ok=False, message="User not found")

        if not await security.verify_password(password, result.password):
            return MessageResponse(ok=False, message="Incorrect password")

        access_token = await security.create_access_token(user_id=result.id, expires_delta=None)
        return LoginSuccess(ok=True, access_token=access_token, token_type="bearer")
