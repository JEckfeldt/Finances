from calendar import monthrange
from datetime import UTC, date, datetime
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

RECENT_TRANSACTION_LIMIT = 5
BUDGET_OVERVIEW_LIMIT = 5
DEFAULT_TREND_MONTH_COUNT = 6


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


def _decimal_scalar(value) -> Decimal:
    return Decimal(str(value))


def _fetch_period_income_expense_totals(
    db: Session,
    user_id: int,
    start_date: date | None,
    end_date: date | None,
) -> tuple[Decimal, Decimal]:
    """Single query for income and expense sums over an optional date range."""
    stmt = select(
        func.coalesce(
            func.sum(Transaction.amount).filter(
                Transaction.type == TransactionType.INCOME
            ),
            0,
        ),
        func.coalesce(
            func.sum(Transaction.amount).filter(
                Transaction.type == TransactionType.EXPENSE
            ),
            0,
        ),
    ).where(Transaction.user_id == user_id)
    stmt = _apply_transaction_date_filters(stmt, start_date, end_date)
    income, expenses = db.execute(stmt).one()
    return _decimal_scalar(income), _decimal_scalar(expenses)


def _fetch_balance_and_monthly_summary_totals(
    db: Session,
    user_id: int,
    month_start: date,
    month_end: date,
) -> tuple[Decimal, Decimal, Decimal, Decimal]:
    """
    Single query for all-time income/expense totals and current-month summary totals.
    """
    stmt = select(
        func.coalesce(
            func.sum(Transaction.amount).filter(
                Transaction.type == TransactionType.INCOME
            ),
            0,
        ),
        func.coalesce(
            func.sum(Transaction.amount).filter(
                Transaction.type == TransactionType.EXPENSE
            ),
            0,
        ),
        func.coalesce(
            func.sum(Transaction.amount).filter(
                Transaction.type == TransactionType.INCOME,
                Transaction.transaction_date >= month_start,
                Transaction.transaction_date <= month_end,
            ),
            0,
        ),
        func.coalesce(
            func.sum(Transaction.amount).filter(
                Transaction.type == TransactionType.EXPENSE,
                Transaction.transaction_date >= month_start,
                Transaction.transaction_date <= month_end,
            ),
            0,
        ),
    ).where(Transaction.user_id == user_id)
    row = db.execute(stmt).one()
    return tuple(_decimal_scalar(value) for value in row)


def _fetch_monthly_income_expense_trends(
    db: Session,
    user_id: int,
    start_date: date | None,
    end_date: date | None,
) -> tuple[dict[tuple[int, int], Decimal], dict[tuple[int, int], Decimal]]:
    """Single grouped query for monthly income and expense trend totals."""
    month_bucket = func.date_trunc(
        "month", cast(Transaction.transaction_date, DateTime)
    ).label("month_bucket")
    stmt = select(
        month_bucket,
        func.coalesce(
            func.sum(Transaction.amount).filter(
                Transaction.type == TransactionType.INCOME
            ),
            0,
        ),
        func.coalesce(
            func.sum(Transaction.amount).filter(
                Transaction.type == TransactionType.EXPENSE
            ),
            0,
        ),
    ).where(Transaction.user_id == user_id)
    stmt = _apply_transaction_date_filters(stmt, start_date, end_date)
    stmt = stmt.group_by(month_bucket)

    income_by_month: dict[tuple[int, int], Decimal] = {}
    expense_by_month: dict[tuple[int, int], Decimal] = {}
    for month_value, income, expenses in db.execute(stmt).all():
        key = (month_value.year, month_value.month)
        income_by_month[key] = _decimal_scalar(income)
        expense_by_month[key] = _decimal_scalar(expenses)

    return income_by_month, expense_by_month


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

    if has_date_filter:
        period_income, period_expenses = _fetch_period_income_expense_totals(
            db, user_id, start_date, end_date
        )
        current_balance = period_income - period_expenses
        summary = MonthlySummary(income=period_income, expenses=period_expenses)
    else:
        now = datetime.now(UTC).date()
        month_start, month_end = _month_date_bounds(now.year, now.month)
        (
            total_income,
            total_expenses,
            month_income,
            month_expenses,
        ) = _fetch_balance_and_monthly_summary_totals(
            db, user_id, month_start, month_end
        )
        current_balance = total_income - total_expenses
        summary = MonthlySummary(income=month_income, expenses=month_expenses)

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

    budget_overview = sorted(
        get_budget_progress_for_user(db, user_id),
        key=lambda budget: budget.percentage,
        reverse=True,
    )[:BUDGET_OVERVIEW_LIMIT]

    income_by_month, expense_by_month = _fetch_monthly_income_expense_trends(
        db, user_id, start_date, end_date
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
