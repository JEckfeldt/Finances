from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.budget import Budget
from app.models.transaction import Transaction, TransactionType
from app.schemas.budget import BudgetProgressResponse


def get_budget_progress_for_user(
    db: Session, user_id: int
) -> list[BudgetProgressResponse]:
    budgets = list(
        db.scalars(
            select(Budget)
            .where(Budget.user_id == user_id)
            .order_by(Budget.category)
        ).all()
    )

    spent_rows = db.execute(
        select(Transaction.category, func.coalesce(func.sum(Transaction.amount), 0))
        .where(
            Transaction.user_id == user_id,
            Transaction.type == TransactionType.EXPENSE,
        )
        .group_by(Transaction.category)
    ).all()
    spent_by_category = {category: Decimal(str(total)) for category, total in spent_rows}

    progress: list[BudgetProgressResponse] = []
    for budget in budgets:
        spent = spent_by_category.get(budget.category, Decimal("0"))
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
