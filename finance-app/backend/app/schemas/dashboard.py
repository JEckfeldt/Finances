from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.models.transaction import TransactionType
from app.schemas.budget import BudgetProgressResponse


class MonthlySummary(BaseModel):
    income: Decimal
    expenses: Decimal


class DashboardRecentTransaction(BaseModel):
    id: int
    description: str
    amount: Decimal
    type: TransactionType
    category: str
    created_at: datetime

    model_config = {"from_attributes": True}


class MonthlySpendingTrend(BaseModel):
    month: str
    total_expenses: Decimal


class DashboardResponse(BaseModel):
    current_balance: Decimal
    monthly_summary: MonthlySummary
    recent_transactions: list[DashboardRecentTransaction]
    budget_overview: list[BudgetProgressResponse]
    monthly_spending_trend: list[MonthlySpendingTrend]
