"""
Natural language financial actions service.

Architecture and security:
- Receives only the authenticated user's ID from routes (same pattern as insights).
- Calls Gemini to interpret user messages into structured JSON intents.
- Does not access the database or create transactions/budgets (parsing only).
- Gemini has no database access; only the user's message is sent in the prompt.
"""

import json
import logging
from typing import Any

from pydantic import TypeAdapter, ValidationError
from sqlalchemy.orm import Session

from app.schemas.ai import (
    AIActionParsed,
    AIActionResponse,
    CreateBudgetAction,
    CreateTransactionAction,
    UnknownAction,
)
from app.services.ai_service import AIServiceError, generate_text

logger = logging.getLogger(__name__)

_ACTION_ADAPTER = TypeAdapter(AIActionParsed)

PARSE_ERROR_MESSAGE = (
    "Could not parse the AI response as a valid financial action. Please try again."
)


def build_action_prompt(message: str) -> str:
    return f"""You are a financial action parser. Interpret the user's message and return ONLY valid JSON with no markdown, code fences, or extra text.

Rules:
- Return a single JSON object and nothing else.
- Use only these intent values: create_transaction, create_budget, unknown
- Infer expense vs income from context (spending/paid/bought = expense; earned/received salary = income).
- Use title case for categories (e.g. "Dining", "Gas", "Salary").
- For dates, use "today" when no specific date is given, otherwise YYYY-MM-DD.
- If the message does not clearly request creating a transaction or budget, return intent unknown.
- Do not invent amounts or categories that are not implied by the message.

Supported JSON shapes:

create_transaction:
{{
  "intent": "create_transaction",
  "amount": 45.67,
  "type": "expense",
  "category": "Dining",
  "description": "Dinner",
  "date": "today"
}}

create_budget:
{{
  "intent": "create_budget",
  "category": "Gas",
  "limit_amount": 500
}}

unknown:
{{
  "intent": "unknown",
  "reason": "Brief explanation"
}}

User message:
{message}
"""


def _strip_json_fence(text: str) -> str:
    stripped = text.strip()
    if not stripped.startswith("```"):
        return stripped

    lines = stripped.splitlines()
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines).strip()


def _load_json_object(text: str) -> dict[str, Any]:
    cleaned = _strip_json_fence(text)
    data = json.loads(cleaned)
    if not isinstance(data, dict):
        raise ValueError("AI response must be a JSON object")
    return data


def parse_action_json(text: str) -> AIActionParsed:
    """Parse Gemini JSON output into a strongly typed action model."""
    data = _load_json_object(text)
    intent = data.get("intent")

    if intent not in {"create_transaction", "create_budget", "unknown"}:
        return UnknownAction(
            intent="unknown",
            reason=(
                f"Unsupported intent: {intent!r}"
                if intent is not None
                else "Missing intent field"
            ),
        )

    try:
        return _ACTION_ADAPTER.validate_python(data)
    except ValidationError as exc:
        logger.warning("AI action JSON failed validation: %s", exc)
        raise ValueError("AI response failed action validation") from exc


def process_natural_language_action(
    db: Session,
    user_id: int,
    message: str,
) -> AIActionResponse:
    """Interpret a natural language message via Gemini and return structured action data."""
    _ = db, user_id

    ai_response = generate_text(build_action_prompt(message))
    if not ai_response.enabled:
        return AIActionResponse(
            enabled=False,
            status="disabled",
            message=ai_response.message,
            action=None,
        )

    if not ai_response.text:
        raise AIServiceError("AI service returned an empty response. Please try again later.")

    try:
        action = parse_action_json(ai_response.text)
    except (json.JSONDecodeError, ValueError, TypeError) as exc:
        logger.warning("Failed to parse AI action response: %s", exc)
        return AIActionResponse(
            enabled=True,
            status="parse_error",
            message=PARSE_ERROR_MESSAGE,
            action=None,
        )

    return AIActionResponse(
        enabled=True,
        status="success",
        action=action,
    )
