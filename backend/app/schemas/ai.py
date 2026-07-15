from pydantic import BaseModel, Field


class AIPromptRequest(BaseModel):
    """Request body for future AI text-generation endpoints."""

    prompt: str = Field(..., min_length=1, max_length=32000)


class AIGenerateTextResponse(BaseModel):
    """Response from the AI service layer."""

    enabled: bool
    text: str | None = None
    message: str | None = None


class AIErrorResponse(BaseModel):
    """Standard error shape for future AI endpoints."""

    detail: str
