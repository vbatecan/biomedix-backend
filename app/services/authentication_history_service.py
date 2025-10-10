from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import AuthenticationHistory


class AuthenticationHistoryService:

    @staticmethod
    async def add_auth_access(db: AsyncSession, user_id: int):
        history = AuthenticationHistory(
            user_id=user_id,
            time_authenticated=datetime.now(),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        db.add(history)
        await db.commit()
        await db.refresh(history)

        return history

    @staticmethod
    async def get_history(db: AsyncSession, page: int = 0, size: int = 10):
        offset = page * size
        result = await db.execute(
            select(AuthenticationHistory)
            .limit(size)
            .offset(offset)
        )
        return result.scalars().all()
