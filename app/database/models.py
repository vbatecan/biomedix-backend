from datetime import datetime
from typing import List

from sqlalchemy import Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import mapped_column, DeclarativeBase, Mapped, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    face_name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(unique=True, index=True)
    password: Mapped[str] = mapped_column(String(60))
    is_active: Mapped[bool] = mapped_column(default=True)
    role: Mapped[str] = mapped_column(String(20))
    transactions: Mapped[List["Transaction"]] = relationship(back_populates="user")
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())


class Medicine(Base):
    __tablename__ = "medicines"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    description: Mapped[str] = mapped_column(String(255))
    stock: Mapped[int] = mapped_column(Integer)
    image_path: Mapped[str] = mapped_column(String(255))
    transaction_details: Mapped[List["TransactionDetail"]] = relationship(back_populates="medicine")
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())


class Transaction(Base):
    __tablename__ = "transactions"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship("User", back_populates="transactions")
    mode: Mapped[str] = mapped_column(String(10))
    transaction_details: Mapped[List["TransactionDetail"]] = relationship(back_populates="transaction")
    transaction_date: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())


class TransactionDetail(Base):
    __tablename__ = "transaction_details"

    id: Mapped[int] = mapped_column(primary_key=True)
    transaction_id: Mapped[int] = mapped_column(ForeignKey("transactions.id"))
    transaction: Mapped["Transaction"] = relationship(back_populates="transaction_details")
    medicine_id: Mapped[int] = mapped_column(ForeignKey("medicines.id"))
    medicine: Mapped["Medicine"] = relationship(back_populates="transaction_details")
    quantity: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())


class AuthenticationHistory(Base):
    __tablename__ = "authentication_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    time_authenticated: Mapped[datetime] = mapped_column(server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
