from sqlalchemy.orm import Session

from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate


def create_transaction_for_user(
    db: Session,
    user_id: int,
    transaction_in: TransactionCreate,
) -> Transaction:
    """Create a transaction for the given user."""
    transaction = Transaction(
        user_id=user_id,
        description=transaction_in.description,
        amount=transaction_in.amount,
        type=transaction_in.type,
        category=transaction_in.category,
        transaction_date=transaction_in.transaction_date,
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction
