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
from google.genai.errors import APIError

from app.core.config import settings
from app.schemas.ai import AIGenerateTextResponse

logger = logging.getLogger(__name__)


class AIServiceError(Exception):
    """Raised when an AI provider request fails."""


def public_ai_error_message(exc: Exception) -> str:
    """Map provider errors to safe client-facing messages."""
    if isinstance(exc, APIError):
        if exc.code == 429:
            return "AI service rate limit exceeded. Please try again later."
        if 500 <= exc.code < 600:
            return "AI service is temporarily unavailable. Please try again later."
        if 400 <= exc.code < 500:
            return "AI request failed. Please try again later."
    return "Failed to generate AI response. Please try again later."


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
        raise AIServiceError("AI provider is not available")

    if not settings.GEMINI_API_KEY:
        raise AIServiceError("AI service is not configured")

    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    try:
        response = client.models.generate_content(
            model=settings.AI_MODEL,
            contents=prompt,
        )
    except Exception as exc:
        logger.exception("Gemini API request failed")
        raise AIServiceError(public_ai_error_message(exc)) from exc

    text = (response.text or "").strip()
    if not text:
        raise AIServiceError("AI service returned an empty response. Please try again later.")

    return AIGenerateTextResponse(enabled=True, text=text)
