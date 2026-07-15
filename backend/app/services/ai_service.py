"""
Gemini integration for future AI financial features.

Architecture and security:
- AI calls happen only from the backend. GEMINI_API_KEY must never be exposed to the frontend.
- User financial data must be filtered and summarized by callers before being included in prompts.
- This module never accesses the database or reads user records directly.
- Future routes/services should build sanitized financial context, then pass plain-text prompts here.
"""

import logging

from google import genai

from app.core.config import settings
from app.schemas.ai import AIGenerateTextResponse

logger = logging.getLogger(__name__)


class AIServiceError(Exception):
    """Raised when an AI provider request fails."""


def generate_text(prompt: str) -> AIGenerateTextResponse:
    """
    Send a prompt to the configured AI provider and return generated text.

    When AI is disabled, returns a response with enabled=False and an explanatory message.
    """
    if not settings.AI_ENABLED:
        return AIGenerateTextResponse(
            enabled=False,
            message="AI features are disabled. Set AI_ENABLED=true to enable.",
        )

    if settings.AI_PROVIDER != "gemini":
        raise AIServiceError(f"Unsupported AI provider: {settings.AI_PROVIDER}")

    if not settings.GEMINI_API_KEY:
        raise AIServiceError("GEMINI_API_KEY is required when AI is enabled")

    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    try:
        response = client.models.generate_content(
            model=settings.AI_MODEL,
            contents=prompt,
        )
    except Exception as exc:
        logger.exception("Gemini API request failed")
        raise AIServiceError("Failed to generate AI response") from exc

    text = (response.text or "").strip()
    if not text:
        raise AIServiceError("Gemini returned an empty response")

    return AIGenerateTextResponse(enabled=True, text=text)
