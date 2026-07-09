from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

from app.core.categories import normalize_category
from app.models.transaction import TransactionType


class TransactionCreate(BaseModel):
    description: str = Field(..., min_length=1, max_length=255)
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    type: TransactionType
    category: str = Field(..., min_length=1, max_length=100)
    transaction_date: date

    @field_validator("description")
    @classmethod
    def strip_description(cls, value: str) -> str:
        return value.strip()

    @field_validator("category")
    @classmethod
    def normalize_category_field(cls, value: str) -> str:
        normalized = normalize_category(value)
        if not normalized:
            raise ValueError("Category is required")
        return normalized


class TransactionUpdate(BaseModel):
    description: str = Field(..., min_length=1, max_length=255)
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    type: TransactionType
    category: str = Field(..., min_length=1, max_length=100)
    transaction_date: date

    @field_validator("description")
    @classmethod
    def strip_description(cls, value: str) -> str:
        return value.strip()

    @field_validator("category")
    @classmethod
    def normalize_category_field(cls, value: str) -> str:
        normalized = normalize_category(value)
        if not normalized:
            raise ValueError("Category is required")
        return normalized


class TransactionResponse(BaseModel):
    id: int
    user_id: int
    description: str
    amount: Decimal
    type: TransactionType
    category: str
    transaction_date: date
    created_at: datetime

    model_config = {"from_attributes": True}
