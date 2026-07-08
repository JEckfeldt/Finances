from calendar import monthrange
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

from sqlalchemy import DateTime, cast, func, select
from sqlalchemy.orm import Session

from app.models.transaction import Transaction, TransactionType
from app.schemas.budget import BudgetProgressResponse
from app.schemas.dashboard import (
    DashboardRecentTransaction,
    DashboardResponse,
    MonthlyComparisonTrend,
    MonthlySpendingTrend,
    MonthlySummary,
)
from app.services.budget import get_budget_progress_for_user

RECENT_TRANSACTION_LIMIT = 10
DEFAULT_TREND_MONTH_COUNT = 6


def _datetime_start(d: date) -> datetime:
    return datetime(d.year, d.month, d.day, tzinfo=UTC)


def _datetime_end_exclusive(d: date) -> datetime:
    return _datetime_start(d + timedelta(days=1))


def _apply_transaction_date_filters(
    stmt,
    start_date: date | None,
    end_date: date | None,
):
    if start_date is not None:
        stmt = stmt.where(Transaction.transaction_date >= start_date)
    if end_date is not None:
        stmt = stmt.where(Transaction.transaction_date <= end_date)
    return stmt


def _sum_by_type(
    db: Session,
    user_id: int,
    transaction_type: TransactionType,
    start_date: date | None = None,
    end_date: date | None = None,
) -> Decimal:
    stmt = select(func.coalesce(func.sum(Transaction.amount), 0)).where(
        Transaction.user_id == user_id,
        Transaction.type == transaction_type,
    )
    stmt = _apply_transaction_date_filters(stmt, start_date, end_date)
    total = db.scalar(stmt)
    return Decimal(str(total))


def _months_in_range(
    start_date: date | None,
    end_date: date | None,
    default_count: int,
) -> list[tuple[int, int]]:
    if start_date is None and end_date is None:
        return _recent_months(default_count)

    range_start = start_date or date(2000, 1, 1)
    range_end = end_date or datetime.now(UTC).date()

    year, month = range_start.year, range_start.month
    end_year, end_month = range_end.year, range_end.month
    months: list[tuple[int, int]] = []

    while (year, month) <= (end_year, end_month):
        months.append((year, month))
        month += 1
        if month > 12:
            month = 1
            year += 1

    return months


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


def _month_date_bounds(year: int, month: int) -> tuple[date, date]:
    last_day = monthrange(year, month)[1]
    return date(year, month, 1), date(year, month, last_day)


def _totals_by_month_and_type(
    db: Session,
    user_id: int,
    transaction_type: TransactionType,
    start_date: date | None,
    end_date: date | None,
) -> dict[tuple[int, int], Decimal]:
    month_bucket = func.date_trunc(
        "month", cast(Transaction.transaction_date, DateTime)
    ).label("month_bucket")
    stmt = select(
        month_bucket,
        func.coalesce(func.sum(Transaction.amount), 0),
    ).where(
        Transaction.user_id == user_id,
        Transaction.type == transaction_type,
    )
    stmt = _apply_transaction_date_filters(stmt, start_date, end_date)
    stmt = stmt.group_by(month_bucket)

    rows = db.execute(stmt).all()
    return {(row[0].year, row[0].month): Decimal(str(row[1])) for row in rows}


def get_dashboard_for_user(
    db: Session,
    user_id: int,
    start_date: date | None = None,
    end_date: date | None = None,
) -> DashboardResponse:
    has_date_filter = start_date is not None or end_date is not None
    budget_start_dt = _datetime_start(start_date) if start_date else None
    budget_end_dt = _datetime_end_exclusive(end_date) if end_date else None

    if has_date_filter:
        period_income = _sum_by_type(
            db, user_id, TransactionType.INCOME, start_date, end_date
        )
        period_expenses = _sum_by_type(
            db, user_id, TransactionType.EXPENSE, start_date, end_date
        )
        current_balance = period_income - period_expenses
        summary = MonthlySummary(income=period_income, expenses=period_expenses)
    else:
        total_income = _sum_by_type(db, user_id, TransactionType.INCOME)
        total_expenses = _sum_by_type(db, user_id, TransactionType.EXPENSE)
        current_balance = total_income - total_expenses

        now = datetime.now(UTC).date()
        month_start, month_end = _month_date_bounds(now.year, now.month)
        summary = MonthlySummary(
            income=_sum_by_type(
                db, user_id, TransactionType.INCOME, month_start, month_end
            ),
            expenses=_sum_by_type(
                db, user_id, TransactionType.EXPENSE, month_start, month_end
            ),
        )

    recent_stmt = (
        select(Transaction)
        .where(Transaction.user_id == user_id)
        .order_by(
            Transaction.transaction_date.desc(),
            Transaction.created_at.desc(),
        )
        .limit(RECENT_TRANSACTION_LIMIT)
    )
    recent_stmt = _apply_transaction_date_filters(recent_stmt, start_date, end_date)
    recent_transactions = list(db.scalars(recent_stmt).all())

    budget_overview = get_budget_progress_for_user(
        db, user_id, start_dt=budget_start_dt, end_dt=budget_end_dt
    )

    income_by_month = _totals_by_month_and_type(
        db, user_id, TransactionType.INCOME, start_date, end_date
    )
    expense_by_month = _totals_by_month_and_type(
        db, user_id, TransactionType.EXPENSE, start_date, end_date
    )

    month_keys = _months_in_range(start_date, end_date, DEFAULT_TREND_MONTH_COUNT)

    monthly_spending_trend: list[MonthlySpendingTrend] = []
    monthly_comparison_trend: list[MonthlyComparisonTrend] = []

    for year, month in month_keys:
        month_label = datetime(year, month, 1, tzinfo=UTC).strftime("%b %Y")
        key = (year, month)
        income = income_by_month.get(key, Decimal("0"))
        expenses = expense_by_month.get(key, Decimal("0"))

        monthly_spending_trend.append(
            MonthlySpendingTrend(month=month_label, total_expenses=expenses)
        )
        monthly_comparison_trend.append(
            MonthlyComparisonTrend(
                month=month_label,
                income=income,
                expenses=expenses,
                net_savings=income - expenses,
            )
        )

    return DashboardResponse(
        current_balance=current_balance,
        monthly_summary=summary,
        recent_transactions=[
            DashboardRecentTransaction.model_validate(transaction)
            for transaction in recent_transactions
        ],
        budget_overview=budget_overview,
        monthly_spending_trend=monthly_spending_trend,
        monthly_comparison_trend=monthly_comparison_trend,
    )
