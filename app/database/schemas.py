from enum import Enum
from typing import Optional

import pydantic
from pydantic import BaseModel, Field
from datetime import datetime

"""
This module defines Pydantic schemas for the database models.
These schemas are used for data validation and serialization.
"""


class ModeEnum(str, Enum):
    IN = "IN"
    OUT = "OUT"


class RoleEnum(str, Enum):
    PHARMACIST = "PHARMACIST"
    IT_ADMIN = "IT_ADMIN"


class UserSchema(pydantic.BaseModel):
    id: int
    face_name: str
    email: str  # We will use the email as username
    is_active: bool
    role: RoleEnum
    created_at: datetime
    updated_at: datetime

class UserInputSchema(BaseModel):
    face_name: str
    email: str  # We will use the email as username
    password: str
    is_active: bool = True
    role: RoleEnum = RoleEnum.PHARMACIST

    def __init__(self, **data):
        super().__init__(**data)
        self.email = self.email
        self.password = self.password
        self.is_active = self.is_active
        self.role = self.role



class MedicineSchema(pydantic.BaseModel):
    id: int
    name: str = Field(..., max_length=255)
    description: str = Field(..., max_length=10000)
    stock: int = Field(...)
    image_path: Optional[str] = Field(..., max_length=255)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)

    class Config:
        orm_mode = True


class TransactionSchema(pydantic.BaseModel):
    id: int
    user_id: int
    mode: ModeEnum
    created_at: datetime
    updated_at: datetime


class TransactionDetailSchema(pydantic.BaseModel):
    id: int
    transaction_id: int
    medicine_id: int
    quantity: int
    price: float
    created_at: datetime
    updated_at: datetime


class MessageResponse(BaseModel):
    ok: bool
    message: str
