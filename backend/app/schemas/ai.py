from decimal import Decimal
from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field, Tag


class AIPromptRequest(BaseModel):
    """Request body for future AI text-generation endpoints."""

    prompt: str = Field(..., min_length=1, max_length=32000)


class AIGenerateTextResponse(BaseModel):
    """Response from the AI service layer."""

    enabled: bool
    text: str | None = None
    message: str | None = None


class AIInsightsResponse(BaseModel):
    """Personalized financial insights for the authenticated user."""

    enabled: bool
    insights: str | None = None
    message: str | None = None


class AIErrorResponse(BaseModel):
    """Standard error shape for AI endpoints."""

    detail: str


class AIActionRequest(BaseModel):
    """Natural language financial action request."""

    message: str = Field(..., min_length=1, max_length=32000)


class CreateTransactionAction(BaseModel):
    """Parsed intent to create a transaction."""

    intent: Literal["create_transaction"]
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    type: Literal["income", "expense"]
    category: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=255)
    date: str = Field(..., min_length=1, max_length=32)


class CreateBudgetAction(BaseModel):
    """Parsed intent to create a budget."""

    intent: Literal["create_budget"]
    category: str = Field(..., min_length=1, max_length=100)
    limit_amount: Decimal = Field(..., gt=0, decimal_places=2)


class UnknownAction(BaseModel):
    """Parsed intent that could not be mapped to a supported action."""

    intent: Literal["unknown"]
    reason: str | None = Field(default=None, max_length=500)


AIActionParsed = Annotated[
    Union[
        Annotated[CreateTransactionAction, Tag("create_transaction")],
        Annotated[CreateBudgetAction, Tag("create_budget")],
        Annotated[UnknownAction, Tag("unknown")],
    ],
    Field(discriminator="intent"),
]


class AIActionResponse(BaseModel):
    """Response from natural language financial action processing."""

    enabled: bool
    status: Literal["success", "disabled", "parse_error"]
    message: str | None = None
    action: CreateTransactionAction | CreateBudgetAction | UnknownAction | None = None
