from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import get_current_user_id
from app.db.session import get_db
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionResponse

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("", response_model=list[TransactionResponse])
def list_transactions(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
) -> list[Transaction]:
    stmt = (
        select(Transaction)
        .where(Transaction.user_id == user_id)
        .order_by(Transaction.created_at.desc())
    )
    return list(db.scalars(stmt).all())


@router.post("", response_model=TransactionResponse, status_code=201)
def create_transaction(
    transaction_in: TransactionCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
) -> Transaction:
    transaction = Transaction(
        user_id=user_id,
        description=transaction_in.description,
        amount=transaction_in.amount,
        type=transaction_in.type,
        category=transaction_in.category,
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction
