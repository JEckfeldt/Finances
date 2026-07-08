from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

from app.core.categories import normalize_category


class BudgetCreate(BaseModel):
    category: str = Field(..., min_length=1, max_length=100)
    limit_amount: Decimal = Field(..., gt=0, decimal_places=2)

    @field_validator("category")
    @classmethod
    def normalize_category_field(cls, value: str) -> str:
        normalized = normalize_category(value)
        if not normalized:
            raise ValueError("Category is required")
        return normalized


class BudgetUpdate(BaseModel):
    category: str = Field(..., min_length=1, max_length=100)
    limit_amount: Decimal = Field(..., gt=0, decimal_places=2)

    @field_validator("category")
    @classmethod
    def normalize_category_field(cls, value: str) -> str:
        normalized = normalize_category(value)
        if not normalized:
            raise ValueError("Category is required")
        return normalized


class BudgetResponse(BaseModel):
    id: int
    user_id: int
    category: str
    limit_amount: Decimal
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BudgetProgressResponse(BaseModel):
    category: str
    limit_amount: Decimal
    spent: Decimal
    remaining: Decimal
    percentage: float
