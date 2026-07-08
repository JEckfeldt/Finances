from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.models.transaction import TransactionType


class TransactionCreate(BaseModel):
    description: str = Field(..., min_length=1, max_length=255)
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    type: TransactionType
    category: str = Field(..., min_length=1, max_length=100)


class TransactionResponse(BaseModel):
    id: int
    user_id: int
    description: str
    amount: Decimal
    type: TransactionType
    category: str
    created_at: datetime

    model_config = {"from_attributes": True}
