from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.session import get_db
from app.models.budget import Budget
from app.models.user import User
from app.schemas.budget import (
    BudgetCreate,
    BudgetProgressResponse,
    BudgetResponse,
    BudgetUpdate,
)

from app.services.budget import get_budget_progress_for_user

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
    return get_budget_progress_for_user(db, current_user.id)


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
