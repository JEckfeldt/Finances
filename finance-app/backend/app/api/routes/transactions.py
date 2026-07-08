import math

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.session import get_db
from app.models.transaction import Transaction, TransactionType
from app.models.user import User
from app.schemas.transaction import (
    TransactionCreate,
    TransactionResponse,
    TransactionUpdate,
)
from app.schemas.transaction_list import TransactionListResponse

router = APIRouter(prefix="/transactions", tags=["transactions"])

SORT_COLUMNS = {
    "date": Transaction.created_at,
    "amount": Transaction.amount,
    "category": Transaction.category,
}


def _get_user_transaction(
    db: Session, user_id: int, transaction_id: int
) -> Transaction | None:
    return db.scalar(
        select(Transaction).where(
            Transaction.id == transaction_id,
            Transaction.user_id == user_id,
        )
    )


def _build_list_query(
    user_id: int,
    search: str | None,
    transaction_type: TransactionType | None,
    category: str | None,
):
    stmt = select(Transaction).where(Transaction.user_id == user_id)

    if search:
        pattern = f"%{search.strip()}%"
        stmt = stmt.where(
            or_(
                Transaction.description.ilike(pattern),
                Transaction.category.ilike(pattern),
            )
        )

    if transaction_type is not None:
        stmt = stmt.where(Transaction.type == transaction_type)

    if category:
        stmt = stmt.where(
            func.lower(Transaction.category) == category.strip().lower()
        )

    return stmt


@router.get("/categories", response_model=list[str])
def list_transaction_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[str]:
    rows = db.scalars(
        select(Transaction.category)
        .where(Transaction.user_id == current_user.id)
        .distinct()
        .order_by(Transaction.category)
    ).all()
    return list(rows)


@router.get("", response_model=TransactionListResponse)
def list_transactions(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    sort_by: str = Query(default="date"),
    sort_order: str = Query(default="desc"),
    search: str | None = Query(default=None),
    transaction_type: TransactionType | None = Query(default=None, alias="type"),
    category: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TransactionListResponse:
    if sort_by not in SORT_COLUMNS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid sort_by value",
        )
    if sort_order not in {"asc", "desc"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid sort_order value",
        )

    base_query = _build_list_query(
        current_user.id, search, transaction_type, category
    )
    total_count = db.scalar(
        select(func.count()).select_from(base_query.subquery())
    )
    total_count = int(total_count or 0)
    total_pages = max(1, math.ceil(total_count / page_size)) if total_count else 0

    sort_column = SORT_COLUMNS[sort_by]
    order = sort_column.asc() if sort_order == "asc" else sort_column.desc()

    stmt = (
        base_query.order_by(order)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items = list(db.scalars(stmt).all())

    return TransactionListResponse(
        items=items,
        page=page,
        page_size=page_size,
        total_count=total_count,
        total_pages=total_pages,
    )


@router.post("", response_model=TransactionResponse, status_code=201)
def create_transaction(
    transaction_in: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Transaction:
    transaction = Transaction(
        user_id=current_user.id,
        description=transaction_in.description,
        amount=transaction_in.amount,
        type=transaction_in.type,
        category=transaction_in.category,
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


@router.put("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    transaction_in: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Transaction:
    transaction = _get_user_transaction(db, current_user.id, transaction_id)
    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found"
        )

    transaction.description = transaction_in.description
    transaction.amount = transaction_in.amount
    transaction.type = transaction_in.type
    transaction.category = transaction_in.category
    db.commit()
    db.refresh(transaction)
    return transaction


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    transaction = _get_user_transaction(db, current_user.id, transaction_id)
    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found"
        )

    db.delete(transaction)
    db.commit()
