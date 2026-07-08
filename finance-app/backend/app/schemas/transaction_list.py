from pydantic import BaseModel

from app.schemas.transaction import TransactionResponse


class TransactionListResponse(BaseModel):
    items: list[TransactionResponse]
    page: int
    page_size: int
    total_count: int
    total_pages: int
