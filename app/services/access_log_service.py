from datetime import datetime

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models import AccessLog
from app.database.schemas import CreateAccessLogSchema


class AccessLogService:

    @staticmethod
    async def create_access_log(db: AsyncSession, log_data: CreateAccessLogSchema) -> AccessLog:
        access_log = AccessLog(
            user_id=log_data.user_id,
            action=log_data.action,
            timestamp=datetime.now()
        )
        db.add(access_log)
        await db.commit()
        
        query = (
            select(AccessLog)
            .options(selectinload(AccessLog.user))
            .where(AccessLog.id == access_log.id)
        )
        result = await db.execute(query)
        return result.scalar_one()

    @staticmethod
    async def get_access_logs(db: AsyncSession, limit: int = 50, offset: int = 0):
        query = (
            select(AccessLog)
            .options(selectinload(AccessLog.user))
            .order_by(desc(AccessLog.timestamp))
            .limit(limit)
            .offset(offset)
        )
        result = await db.execute(query)
        return result.scalars().all()
