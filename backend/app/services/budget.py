from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.budget import Budget
from app.models.transaction import Transaction, TransactionType
from app.schemas.budget import BudgetCreate, BudgetProgressResponse


def _current_month_bounds() -> tuple[date, date]:
    """Return [month_start, next_month_start) for the server's current calendar month."""
    today = datetime.now(UTC).date()
    month_start = date(today.year, today.month, 1)
    if today.month == 12:
        next_month_start = date(today.year + 1, 1, 1)
    else:
        next_month_start = date(today.year, today.month + 1, 1)
    return month_start, next_month_start


def create_budget_for_user(
    db: Session,
    user_id: int,
    budget_in: BudgetCreate,
) -> Budget:
    """Create a budget for the given user."""
    budget = Budget(
        user_id=user_id,
        category=budget_in.category,
        limit_amount=budget_in.limit_amount,
    )
    db.add(budget)
    db.commit()
    db.refresh(budget)
    return budget


def get_budget_progress_for_user(
    db: Session,
    user_id: int,
) -> list[BudgetProgressResponse]:
    budgets = list(
        db.scalars(
            select(Budget)
            .where(Budget.user_id == user_id)
            .order_by(Budget.category)
        ).all()
    )

    month_start, next_month_start = _current_month_bounds()

    stmt = select(
        func.lower(Transaction.category),
        func.coalesce(func.sum(Transaction.amount), 0),
    ).where(
        Transaction.user_id == user_id,
        Transaction.type == TransactionType.EXPENSE,
        Transaction.transaction_date >= month_start,
        Transaction.transaction_date < next_month_start,
    )
    stmt = stmt.group_by(func.lower(Transaction.category))

    spent_rows = db.execute(stmt).all()
    spent_by_category = {
        category.lower(): Decimal(str(total)) for category, total in spent_rows
    }

    progress: list[BudgetProgressResponse] = []
    for budget in budgets:
        spent = spent_by_category.get(budget.category.lower(), Decimal("0"))
        remaining = budget.limit_amount - spent
        percentage = (
            float(spent / budget.limit_amount * 100) if budget.limit_amount > 0 else 0.0
        )
        progress.append(
            BudgetProgressResponse(
                category=budget.category,
                limit_amount=budget.limit_amount,
                spent=spent,
                remaining=remaining,
                percentage=round(percentage, 2),
            )
        )

    return progress
