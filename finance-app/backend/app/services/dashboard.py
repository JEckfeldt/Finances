from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.transaction import Transaction, TransactionType
from app.schemas.budget import BudgetProgressResponse
from app.schemas.dashboard import (
    DashboardRecentTransaction,
    DashboardResponse,
    MonthlySpendingTrend,
    MonthlySummary,
)
from app.services.budget import get_budget_progress_for_user

RECENT_TRANSACTION_LIMIT = 10
TREND_MONTH_COUNT = 6


def _sum_by_type(
    db: Session, user_id: int, transaction_type: TransactionType
) -> Decimal:
    total = db.scalar(
        select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            Transaction.user_id == user_id,
            Transaction.type == transaction_type,
        )
    )
    return Decimal(str(total))


def _monthly_sum_by_type(
    db: Session,
    user_id: int,
    transaction_type: TransactionType,
    month_start: datetime,
    month_end: datetime,
) -> Decimal:
    total = db.scalar(
        select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            Transaction.user_id == user_id,
            Transaction.type == transaction_type,
            Transaction.created_at >= month_start,
            Transaction.created_at < month_end,
        )
    )
    return Decimal(str(total))


def _recent_months(count: int) -> list[tuple[int, int]]:
    now = datetime.now(UTC)
    year, month = now.year, now.month
    months: list[tuple[int, int]] = []
    for _ in range(count):
        months.append((year, month))
        month -= 1
        if month == 0:
            month = 12
            year -= 1
    return list(reversed(months))


def _month_bounds(year: int, month: int) -> tuple[datetime, datetime]:
    start = datetime(year, month, 1, tzinfo=UTC)
    if month == 12:
        end = datetime(year + 1, 1, 1, tzinfo=UTC)
    else:
        end = datetime(year, month + 1, 1, tzinfo=UTC)
    return start, end


def get_dashboard_for_user(db: Session, user_id: int) -> DashboardResponse:
    total_income = _sum_by_type(db, user_id, TransactionType.INCOME)
    total_expenses = _sum_by_type(db, user_id, TransactionType.EXPENSE)
    current_balance = total_income - total_expenses

    now = datetime.now(UTC)
    month_start, month_end = _month_bounds(now.year, now.month)
    monthly_income = _monthly_sum_by_type(
        db, user_id, TransactionType.INCOME, month_start, month_end
    )
    monthly_expenses = _monthly_sum_by_type(
        db, user_id, TransactionType.EXPENSE, month_start, month_end
    )

    recent_transactions = list(
        db.scalars(
            select(Transaction)
            .where(Transaction.user_id == user_id)
            .order_by(Transaction.created_at.desc())
            .limit(RECENT_TRANSACTION_LIMIT)
        ).all()
    )

    budget_overview = get_budget_progress_for_user(db, user_id)

    month_bucket = func.date_trunc("month", Transaction.created_at).label(
        "month_bucket"
    )
    expense_by_month_rows = db.execute(
        select(
            month_bucket,
            func.coalesce(func.sum(Transaction.amount), 0),
        )
        .where(
            Transaction.user_id == user_id,
            Transaction.type == TransactionType.EXPENSE,
        )
        .group_by(month_bucket)
    ).all()
    expense_by_month = {
        (row[0].year, row[0].month): Decimal(str(row[1])) for row in expense_by_month_rows
    }

    monthly_spending_trend: list[MonthlySpendingTrend] = []
    for year, month in _recent_months(TREND_MONTH_COUNT):
        month_label = datetime(year, month, 1, tzinfo=UTC).strftime("%b %Y")
        monthly_spending_trend.append(
            MonthlySpendingTrend(
                month=month_label,
                total_expenses=expense_by_month.get((year, month), Decimal("0")),
            )
        )

    return DashboardResponse(
        current_balance=current_balance,
        monthly_summary=MonthlySummary(
            income=monthly_income,
            expenses=monthly_expenses,
        ),
        recent_transactions=[
            DashboardRecentTransaction.model_validate(transaction)
            for transaction in recent_transactions
        ],
        budget_overview=budget_overview,
        monthly_spending_trend=monthly_spending_trend,
    )
