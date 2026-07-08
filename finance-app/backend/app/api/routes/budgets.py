from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.session import get_db
from app.models.budget import Budget
from app.models.transaction import Transaction, TransactionType
from app.models.user import User
from app.schemas.budget import (
    BudgetCreate,
    BudgetProgressResponse,
    BudgetResponse,
    BudgetUpdate,
)

router = APIRouter(prefix="/budgets", tags=["budgets"])


def _get_user_budget(
    db: Session, user_id: int, budget_id: int
) -> Budget | None:
    return db.scalar(
        select(Budget).where(Budget.id == budget_id, Budget.user_id == user_id)
    )


@router.get("/progress", response_model=list[BudgetProgressResponse])
def get_budget_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[BudgetProgressResponse]:
    budgets = list(
        db.scalars(
            select(Budget)
            .where(Budget.user_id == current_user.id)
            .order_by(Budget.category)
        ).all()
    )

    spent_rows = db.execute(
        select(Transaction.category, func.coalesce(func.sum(Transaction.amount), 0))
        .where(
            Transaction.user_id == current_user.id,
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


@router.get("", response_model=list[BudgetResponse])
def list_budgets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Budget]:
    stmt = (
        select(Budget)
        .where(Budget.user_id == current_user.id)
        .order_by(Budget.category)
    )
    return list(db.scalars(stmt).all())


@router.post("", response_model=BudgetResponse, status_code=201)
def create_budget(
    budget_in: BudgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Budget:
    budget = Budget(
        user_id=current_user.id,
        category=budget_in.category,
        limit_amount=budget_in.limit_amount,
    )
    db.add(budget)
    db.commit()
    db.refresh(budget)
    return budget


@router.put("/{budget_id}", response_model=BudgetResponse)
def update_budget(
    budget_id: int,
    budget_in: BudgetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Budget:
    budget = _get_user_budget(db, current_user.id, budget_id)
    if budget is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found"
        )

    budget.category = budget_in.category
    budget.limit_amount = budget_in.limit_amount
    db.commit()
    db.refresh(budget)
    return budget


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(
    budget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    budget = _get_user_budget(db, current_user.id, budget_id)
    if budget is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found"
        )

    db.delete(budget)
    db.commit()
