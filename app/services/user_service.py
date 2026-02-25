import os
import app.core.security as security

from sqlalchemy import select, Exists, exists, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import User
from app.database.schemas import UserInputSchema


class UserService:
    @staticmethod
    def _normalize_face_name(face_name: str) -> str:
        normalized = (face_name or "").replace("_", " ").replace("-", " ")
        return " ".join(normalized.strip().split()).lower()

    @staticmethod
    async def get_users(db: AsyncSession, limit: int = 100, offset: int = 0):
        result = await db.execute(
            select(User)
            .limit(limit)
            .offset(offset)
        )
        users = result.scalars().fetchall()
        return users

    @staticmethod
    async def get_user_by_face_name(db: AsyncSession, face_name: str):
        normalized_face_name = UserService._normalize_face_name(face_name)
        if not normalized_face_name:
            return None

        # Fast path for the common case: exact normalized match done in SQL.
        result = await db.execute(
            select(User).where(func.lower(func.trim(User.face_name)) == normalized_face_name)
        )
        user = result.scalar_one_or_none()
        if user:
            return user

        # Fallback: in-memory normalization to handle extra separators or spacing variance.
        result = await db.execute(select(User))
        for candidate in result.scalars().all():
            if UserService._normalize_face_name(candidate.face_name) == normalized_face_name:
                return candidate

        return user

    @staticmethod
    async def create_user(db: AsyncSession, user: UserInputSchema, image):
        db_user = User(
            face_name=user.face_name,
            email=user.email,
            password=await security.hash_password(user.password),
            is_active=user.is_active,
            role=user.role
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)

        folder_path = f"./db/{user.face_name}"
        os.makedirs(folder_path, exist_ok=True)
        image_path = os.path.join(folder_path, f"{user.face_name}.jpg")
        with open(image_path, "wb") as f:
            f.write(image.file.read())

        return db_user

    @staticmethod
    async def delete_user(db: AsyncSession, user_id: int):
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if user:
            await db.delete(user)
            await db.commit()
        else:
            raise ValueError("User not found")
        return user

    @staticmethod
    async def toggle_active_status(db: AsyncSession, user_id: int, is_active: bool):
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if user.is_active == is_active:
            return user

        if user:
            user.is_active = is_active
            db.add(user)
            await db.commit()
            await db.refresh(user)
        else:
            raise ValueError("User not found")
        return user

    @staticmethod
    async def is_exist(db: AsyncSession, user_id: int):
        result = (await db.execute(
            exists().where(User.id == user_id)
        )).scalar()

        return result
