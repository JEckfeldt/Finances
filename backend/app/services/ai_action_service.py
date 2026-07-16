"""
Natural language financial actions service.

Architecture and security:
- Receives only the authenticated user's ID from routes (same pattern as insights).
- Calls Gemini to interpret user messages into structured JSON intents.
- Executes supported actions by delegating to existing domain services.
- Never writes directly to the database — creation uses transaction/budget services.
- Gemini has no database access; only the user's message is sent in the prompt.
"""

import json
import logging
import re
from datetime import UTC, date, datetime, timedelta
from typing import Any

from pydantic import TypeAdapter, ValidationError
from sqlalchemy.orm import Session

from app.models.transaction import TransactionType
from app.schemas.ai import (
    AIActionParsed,
    AIActionResponse,
    CreateBudgetAction,
    CreateTransactionAction,
    UnknownAction,
)
from app.schemas.budget import BudgetCreate, BudgetResponse
from app.schemas.transaction import TransactionCreate, TransactionResponse
from app.services.ai_service import AIServiceError, generate_text
from app.services.budget import create_budget_for_user
from app.services.transaction import create_transaction_for_user

logger = logging.getLogger(__name__)

_ACTION_ADAPTER = TypeAdapter(AIActionParsed)

PARSE_ERROR_MESSAGE = (
    "Could not understand that request. Try including an amount and what it was for, "
    "such as \"I spent $42 at Costco\" or \"Make a $250 grocery budget\"."
)
TRANSACTION_VALIDATION_ERROR_MESSAGE = (
    "The transaction details were incomplete or unclear. Include an amount, what you "
    "bought or received, and a category if possible."
)
BUDGET_VALIDATION_ERROR_MESSAGE = (
    "The budget details were incomplete or unclear. Include a category and limit amount, "
    "such as \"Make a $250 grocery budget\"."
)
AMBIGUOUS_ACTION_MESSAGE = (
    "That message was too vague to create a transaction or budget. "
    "Try being more specific about the amount and purpose."
)
TRANSACTION_CREATED_MESSAGE = "Transaction created."
BUDGET_CREATED_MESSAGE = "Budget created."

_GENERIC_DESCRIPTIONS = frozenset(
    {
        "expense",
        "income",
        "transaction",
        "purchase",
        "payment",
        "budget",
        "unknown",
    }
)


def build_action_prompt(message: str) -> str:
    today = datetime.now(UTC).date()
    today_label = today.strftime("%A, %B %d, %Y")

    return f"""You are a financial action parser. Interpret the user's message and return ONLY valid JSON with no markdown, code fences, or extra text.

Reference date (use for all relative date resolution):
- Today is {today.isoformat()} ({today_label}).

Rules:
- Return a single JSON object and nothing else.
- Use only these intent values: create_transaction, create_budget, unknown
- Convert relative dates to YYYY-MM-DD using the reference date above:
  - "today" or "this morning" -> {today.isoformat()}
  - "yesterday" -> previous calendar day
  - "last Friday", "last week", and similar phrases -> best-effort YYYY-MM-DD
- For the date field, prefer YYYY-MM-DD. Use "today" only when the message gives no date clue.
- Infer expense vs income from wording:
  - expense: spent, paid, bought, purchased, cost, charge
  - income: earned, received, got paid, paycheck, salary, deposit
- Map merchant names to descriptions and sensible categories:
  - Costco, Walmart, Target -> Groceries or Shopping (choose the best fit)
  - Gas stations -> Gas
  - Restaurants, lunch, dinner -> Dining
- Use title case for categories (e.g. "Dining", "Gas", "Groceries", "Salary").
- Description should name the merchant or purchase (e.g. "Costco", "Lunch", "Paycheck").
- Budget requests use create_budget. Transaction requests use create_transaction.
- If the amount, category, or purpose is missing or too ambiguous, return intent unknown with a helpful reason.
- Do not invent amounts, merchants, or categories that are not implied by the message.
- Questions, summaries, and general finance chat are intent unknown.

Example mappings:

"I spent $42 at Costco" ->
{{
  "intent": "create_transaction",
  "amount": 42,
  "type": "expense",
  "category": "Groceries",
  "description": "Costco",
  "date": "{today.isoformat()}"
}}

"I got paid $1800" ->
{{
  "intent": "create_transaction",
  "amount": 1800,
  "type": "income",
  "category": "Salary",
  "description": "Paycheck",
  "date": "{today.isoformat()}"
}}

"Make a $250 grocery budget" ->
{{
  "intent": "create_budget",
  "category": "Groceries",
  "limit_amount": 250
}}

"I paid $65 for gas yesterday" ->
{{
  "intent": "create_transaction",
  "amount": 65,
  "type": "expense",
  "category": "Gas",
  "description": "Gas",
  "date": "{(today - timedelta(days=1)).isoformat()}"
}}

"I bought lunch for $17" ->
{{
  "intent": "create_transaction",
  "amount": 17,
  "type": "expense",
  "category": "Dining",
  "description": "Lunch",
  "date": "{today.isoformat()}"
}}

Supported JSON shapes:

create_transaction:
{{
  "intent": "create_transaction",
  "amount": 45.67,
  "type": "expense",
  "category": "Dining",
  "description": "Dinner",
  "date": "{today.isoformat()}"
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
  "reason": "Brief explanation of what is missing or unclear"
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
                f"Unsupported action: {intent!r}"
                if intent is not None
                else "The response did not include a supported action."
            ),
        )

    try:
        return _ACTION_ADAPTER.validate_python(data)
    except ValidationError as exc:
        logger.warning("AI action JSON failed validation: %s", exc)
        raise ValueError("AI response failed action validation") from exc


def resolve_action_date(
    date_str: str,
    *,
    reference: date | None = None,
) -> date:
    """Convert AI date values into a concrete transaction date."""
    ref = reference or datetime.now(UTC).date()
    normalized = date_str.strip().lower()

    if normalized == "today":
        return ref
    if normalized == "yesterday":
        return ref - timedelta(days=1)

    try:
        return date.fromisoformat(date_str.strip())
    except ValueError as exc:
        raise ValueError(f"Invalid date: {date_str}") from exc


def _is_generic_description(description: str, category: str) -> bool:
    description_key = description.strip().lower()
    category_key = category.strip().lower()
    return (
        not description_key
        or description_key in _GENERIC_DESCRIPTIONS
        or description_key == category_key
        and description_key in {"expense", "income", "transaction"}
    )


def validate_transaction_action(action: CreateTransactionAction) -> str | None:
    """Return a user-facing error when parsed transaction data is too ambiguous."""
    if _is_generic_description(action.description, action.category):
        return (
            "Please include what the transaction was for, such as a merchant or purchase "
            "description."
        )

    if not re.search(r"[A-Za-z]", action.description):
        return "Transaction description must include readable text."

    return None


def validate_budget_action(action: CreateBudgetAction) -> str | None:
    """Return a user-facing error when parsed budget data is too ambiguous."""
    if not action.category.strip():
        return "Please include a budget category, such as Groceries or Gas."

    if action.limit_amount <= 0:
        return "Budget limit amount must be greater than zero."

    return None


def transaction_create_from_action(
    action: CreateTransactionAction,
) -> TransactionCreate:
    """Map parsed AI transaction fields into the standard create schema."""
    return TransactionCreate(
        description=action.description,
        amount=action.amount,
        type=TransactionType(action.type),
        category=action.category,
        transaction_date=resolve_action_date(action.date),
    )


def budget_create_from_action(action: CreateBudgetAction) -> BudgetCreate:
    """Map parsed AI budget fields into the standard create schema."""
    return BudgetCreate(
        category=action.category,
        limit_amount=action.limit_amount,
    )


def execute_parsed_action(
    db: Session,
    user_id: int,
    action: AIActionParsed,
) -> AIActionResponse:
    """Execute a parsed action using existing domain services."""
    if isinstance(action, UnknownAction):
        return AIActionResponse(
            enabled=True,
            status="validation_error",
            message=action.reason or AMBIGUOUS_ACTION_MESSAGE,
            action=None,
            transaction=None,
            budget=None,
        )

    if isinstance(action, CreateTransactionAction):
        ambiguity_error = validate_transaction_action(action)
        if ambiguity_error:
            return AIActionResponse(
                enabled=True,
                status="validation_error",
                message=ambiguity_error,
                action=None,
                transaction=None,
                budget=None,
            )

        try:
            transaction_in = transaction_create_from_action(action)
        except (ValidationError, ValueError) as exc:
            logger.warning("AI transaction action failed validation: %s", exc)
            return AIActionResponse(
                enabled=True,
                status="validation_error",
                message=TRANSACTION_VALIDATION_ERROR_MESSAGE,
                action=None,
                transaction=None,
                budget=None,
            )

        transaction = create_transaction_for_user(db, user_id, transaction_in)
        return AIActionResponse(
            enabled=True,
            status="success",
            message=TRANSACTION_CREATED_MESSAGE,
            action=None,
            transaction=TransactionResponse.model_validate(transaction),
            budget=None,
        )

    if isinstance(action, CreateBudgetAction):
        ambiguity_error = validate_budget_action(action)
        if ambiguity_error:
            return AIActionResponse(
                enabled=True,
                status="validation_error",
                message=ambiguity_error,
                action=None,
                transaction=None,
                budget=None,
            )

        try:
            budget_in = budget_create_from_action(action)
        except ValidationError as exc:
            logger.warning("AI budget action failed validation: %s", exc)
            return AIActionResponse(
                enabled=True,
                status="validation_error",
                message=BUDGET_VALIDATION_ERROR_MESSAGE,
                action=None,
                transaction=None,
                budget=None,
            )

        budget = create_budget_for_user(db, user_id, budget_in)
        return AIActionResponse(
            enabled=True,
            status="success",
            message=BUDGET_CREATED_MESSAGE,
            action=None,
            transaction=None,
            budget=BudgetResponse.model_validate(budget),
        )

    return AIActionResponse(
        enabled=True,
        status="validation_error",
        message=AMBIGUOUS_ACTION_MESSAGE,
        action=None,
        transaction=None,
        budget=None,
    )


def process_natural_language_action(
    db: Session,
    user_id: int,
    message: str,
) -> AIActionResponse:
    """Interpret a natural language message and execute supported actions."""
    trimmed_message = message.strip()
    if not trimmed_message:
        return AIActionResponse(
            enabled=True,
            status="validation_error",
            message="Please enter a message describing the transaction or budget.",
            action=None,
            transaction=None,
            budget=None,
        )

    ai_response = generate_text(build_action_prompt(trimmed_message))
    if not ai_response.enabled:
        return AIActionResponse(
            enabled=False,
            status="disabled",
            message=ai_response.message,
            action=None,
            transaction=None,
            budget=None,
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
            transaction=None,
            budget=None,
        )

    return execute_parsed_action(db, user_id, action)
