from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.database.models import Transaction, TransactionDetail
from app.services.user_service import UserService
from app.utils.datetimerange import DateTimeRange


class TransactionService:
    @staticmethod
    async def get_user_transactions(db: AsyncSession, user_id: int, date_range: DateTimeRange, page: int, size: int):
        is_user_exists = await UserService.is_exist(db, user_id)
        if not is_user_exists:
            raise ValueError("User does not exists.")

        result = await db.execute(
            select(Transaction)
            .options(joinedload(Transaction.user))
            .options(joinedload(Transaction.transaction_details).joinedload(TransactionDetail.medicine))
            .where(Transaction.user_id == user_id)
            .where(Transaction.transaction_date >= date_range.start_datetime)
            .where(Transaction.transaction_date <= date_range.end_datetime)
            .limit(size)
            .offset((page - 1) * size)
        )

        return result.unique().scalars().all()

    @staticmethod
    async def all(db: AsyncSession, page: int, size: int):
        result = await db.execute(
            select(Transaction)
            .options(joinedload(Transaction.user))
            .options(joinedload(Transaction.transaction_details).joinedload(TransactionDetail.medicine))
            .limit(size)
            .offset(page * size)
        )

        return result.unique().scalars().all()
