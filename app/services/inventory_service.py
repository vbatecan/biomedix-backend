from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Medicine, Transaction, TransactionDetail
from app.types.MedicineInput import MedicineInput


class InventoryService:

    @staticmethod
    async def log_transaction(db: AsyncSession, medicine_id: int, quantity: int, user_id: int, mode: str):
        transaction = Transaction(user_id=user_id, transaction_date=datetime.now(), mode=mode)
        db.add(transaction)
        await db.commit()

        detail = TransactionDetail(
            transaction_id=transaction.id,
            medicine_id=medicine_id,
            quantity=quantity
        )

        db.add(detail)
        await db.commit()
        await db.refresh(transaction)
        return transaction

    @staticmethod
    async def add_stock(db: AsyncSession, medicine_id: int, increment: int, user_id: int):
        result = await db.execute(
            select(Medicine).where(Medicine.id == medicine_id)
        )
        medicine = result.scalar_one_or_none()

        if medicine is None:
            raise ValueError("Medicine not found")

        medicine.stock += increment
        await db.commit()
        transaction = await InventoryService.log_transaction(db, medicine_id, increment, user_id, mode='IN')

        return transaction

    @staticmethod
    async def list_all(db: AsyncSession, limit: int = 100, offset: int = 0):
        result = await db.execute(
            select(Medicine).limit(limit).offset(offset)
        )
        medicines = result.scalars().all()
        return medicines

    @staticmethod
    async def get_medicine(db: AsyncSession, medicine_id: int):
        result = await db.execute(
            select(Medicine).where(Medicine.id == medicine_id)
        )
        medicine = result.scalar_one_or_none()
        return medicine

    async def search_by_name(db: AsyncSession, name: str):
        result = await db.execute(
            select(Medicine).where(Medicine.name.ilike(f"%{name}%"))
        )
        medicines = result.scalars().all()
        return medicines

    @staticmethod
    async def add_medicine(db: AsyncSession, medicine: MedicineInput, thumbnail_path: str):
        # Check if medicine with the same name already exists
        result = await db.execute(
            select(Medicine).where(Medicine.name == medicine.name)
        )
        existing_medicine = result.scalar_one_or_none()
        if existing_medicine:
            raise ValueError("Medicine with this name already exists")

        new_medicine = Medicine(name=medicine.name, description=medicine.description, stock=medicine.stock, image_path=thumbnail_path)
        db.add(new_medicine)
        await db.commit()
        await db.refresh(new_medicine)
        return new_medicine
