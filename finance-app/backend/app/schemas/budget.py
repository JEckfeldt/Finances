from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class BudgetCreate(BaseModel):
    category: str = Field(..., min_length=1, max_length=100)
    limit_amount: Decimal = Field(..., gt=0, decimal_places=2)


class BudgetUpdate(BaseModel):
    category: str = Field(..., min_length=1, max_length=100)
    limit_amount: Decimal = Field(..., gt=0, decimal_places=2)


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
