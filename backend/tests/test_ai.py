from datetime import UTC, datetime
from unittest.mock import patch

import pytest
from google.genai.errors import ClientError, ServerError

from app.schemas.ai import AIGenerateTextResponse
from app.services.ai_action_service import (
    budget_create_from_action,
    parse_action_json,
    transaction_create_from_action,
)
from app.services.ai_service import AIServiceError, generate_text, public_ai_error_message
from tests.conftest import create_transaction, login_user


def _current_month_date(day: int = 8) -> str:
    today = datetime.now(UTC).date()
    return f"{today.year}-{today.month:02d}-{day:02d}"


def test_insights_requires_authentication(client):
    response = client.post("/ai/insights")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_insights_returns_disabled_response_when_ai_disabled(client, user_a):
    response = client.post("/ai/insights")

    assert response.status_code == 200
    data = response.json()
    assert data["enabled"] is False
    assert data["insights"] is None
    assert "disabled" in data["message"].lower()


@patch("app.services.ai_insights_service.generate_text")
def test_authenticated_user_can_request_insights(
    mock_generate_text, client, user_a
):
    mock_generate_text.return_value = AIGenerateTextResponse(
        enabled=True,
        text="- Reduce dining spending.\n- Increase savings rate.",
    )
    create_transaction(
        client,
        description="Salary",
        amount="2000.00",
        transaction_type="income",
        category="Salary",
        transaction_date=_current_month_date(),
    )
    create_transaction(
        client,
        description="Groceries",
        amount="150.00",
        transaction_date=_current_month_date(),
    )

    response = client.post("/ai/insights")

    assert response.status_code == 200
    data = response.json()
    assert data["enabled"] is True
    assert "dining spending" in data["insights"]
    mock_generate_text.assert_called_once()
    prompt = mock_generate_text.call_args.args[0]
    assert "2000.00" in prompt
    assert "150.00" in prompt
    assert "personal finance assistant" in prompt.lower()
    assert "markdown" in prompt.lower()
    assert "**bold text**" in prompt.lower()


@patch("app.services.ai_insights_service.generate_text")
def test_insights_use_only_authenticated_user_data(
    mock_generate_text, client, user_a, user_b
):
    mock_generate_text.return_value = AIGenerateTextResponse(
        enabled=True,
        text="Insights for the current user only.",
    )

    login_user(client, user_a["email"])
    create_transaction(
        client,
        description="User A groceries",
        amount="42.00",
        transaction_date=_current_month_date(),
    )

    login_user(client, user_b["email"])
    create_transaction(
        client,
        description="User B groceries",
        amount="999.00",
        transaction_date=_current_month_date(),
    )

    login_user(client, user_a["email"])
    response = client.post("/ai/insights")

    assert response.status_code == 200
    prompt = mock_generate_text.call_args.args[0]
    assert "42.00" in prompt
    assert "999.00" not in prompt


@patch("app.services.ai_insights_service.generate_text")
def test_insights_includes_budget_utilization(
    mock_generate_text, client, user_a
):
    mock_generate_text.return_value = AIGenerateTextResponse(
        enabled=True,
        text="Budget insights ready.",
    )
    client.post(
        "/budgets",
        json={"category": "Food", "limit_amount": "500.00"},
    )
    create_transaction(
        client,
        amount="125.00",
        category="Food",
        transaction_date=_current_month_date(),
    )

    response = client.post("/ai/insights")

    assert response.status_code == 200
    prompt = mock_generate_text.call_args.args[0]
    assert "Budget utilization" in prompt
    assert "Food" in prompt
    assert "125.00" in prompt
    assert "500.00" in prompt


@patch("app.services.ai_insights_service.generate_text")
def test_insights_gemini_failure_returns_service_unavailable(
    mock_generate_text, client, user_a
):
    mock_generate_text.side_effect = AIServiceError(
        "AI service is temporarily unavailable. Please try again later."
    )

    response = client.post("/ai/insights")

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "AI service is temporarily unavailable. Please try again later."
    )
    assert "api" not in response.json()["detail"].lower()
    assert "gemini" not in response.json()["detail"].lower()


@patch("app.services.ai_insights_service.generate_text")
def test_insights_rate_limit_failure_returns_clear_message(
    mock_generate_text, client, user_a
):
    mock_generate_text.side_effect = AIServiceError(
        "AI service rate limit exceeded. Please try again later."
    )

    response = client.post("/ai/insights")

    assert response.status_code == 503
    assert "rate limit" in response.json()["detail"].lower()


def test_public_ai_error_message_maps_rate_limit():
    error = ClientError(429, {"error": {"message": "quota exceeded"}}, None)

    message = public_ai_error_message(error)

    assert "rate limit" in message.lower()
    assert "quota" not in message.lower()


def test_public_ai_error_message_maps_server_error():
    error = ServerError(503, {"error": {"message": "unavailable"}}, None)

    message = public_ai_error_message(error)

    assert "temporarily unavailable" in message.lower()


@patch("app.services.ai_service.settings.AI_ENABLED", True)
@patch("app.services.ai_service.settings.GEMINI_API_KEY", "test-key")
@patch("app.services.ai_service.settings.AI_PROVIDER", "gemini")
@patch("app.services.ai_service.settings.AI_MODEL", "gemini-2.0-flash")
@patch("app.services.ai_service.genai.Client")
def test_generate_text_maps_gemini_rate_limit(mock_client_class):
    mock_client = mock_client_class.return_value
    mock_client.models.generate_content.side_effect = ClientError(
        429,
        {"error": {"message": "quota exceeded"}},
        None,
    )

    with pytest.raises(AIServiceError) as exc_info:
        generate_text("Summarize spending")

    assert "rate limit" in str(exc_info.value).lower()


def test_action_requires_authentication(client):
    response = client.post(
        "/ai/action",
        json={"message": "I spent $45 on dinner"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_action_returns_disabled_response_when_ai_disabled(client, user_a):
    response = client.post(
        "/ai/action",
        json={"message": "I spent $45 on dinner"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["enabled"] is False
    assert data["status"] == "disabled"
    assert data["action"] is None
    assert "disabled" in data["message"].lower()


@patch("app.services.ai_action_service.generate_text")
def test_action_creates_transaction_successfully(mock_generate_text, client, user_a):
    mock_generate_text.return_value = AIGenerateTextResponse(
        enabled=True,
        text=(
            '{"intent": "create_transaction", "amount": 42.18, "type": "expense", '
            '"category": "Dining", "description": "Dinner", "date": "today"}'
        ),
    )

    response = client.post(
        "/ai/action",
        json={"message": "I spent $42.18 on dinner"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["enabled"] is True
    assert data["status"] == "success"
    assert data["message"] == "Transaction created."
    assert data["action"] is None
    assert data["transaction"]["amount"] == "42.18"
    assert data["transaction"]["type"] == "expense"
    assert data["transaction"]["category"] == "Dining"
    assert data["transaction"]["description"] == "Dinner"
    assert data["transaction"]["user_id"] == user_a["id"]

    list_response = client.get("/transactions")
    assert list_response.status_code == 200
    items = list_response.json()["items"]
    assert len(items) == 1
    assert items[0]["id"] == data["transaction"]["id"]
    assert items[0]["amount"] == "42.18"

    mock_generate_text.assert_called_once()
    prompt = mock_generate_text.call_args.args[0]
    assert "ONLY valid JSON" in prompt
    assert "create_transaction" in prompt
    assert "I spent $42.18 on dinner" in prompt


@patch("app.services.ai_action_service.generate_text")
def test_action_create_transaction_normalizes_category(
    mock_generate_text, client, user_a
):
    mock_generate_text.return_value = AIGenerateTextResponse(
        enabled=True,
        text=(
            '{"intent": "create_transaction", "amount": 20.00, "type": "expense", '
            '"category": "  dining  ", "description": "Lunch", "date": "today"}'
        ),
    )

    response = client.post(
        "/ai/action",
        json={"message": "I spent $20 on lunch"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["transaction"]["category"] == "Dining"


@patch("app.services.ai_action_service.generate_text")
def test_action_creates_budget_successfully(mock_generate_text, client, user_a):
    mock_generate_text.return_value = AIGenerateTextResponse(
        enabled=True,
        text='{"intent": "create_budget", "category": "Gas", "limit_amount": 500}',
    )

    response = client.post(
        "/ai/action",
        json={"message": "Create a $500 gas budget"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["enabled"] is True
    assert data["status"] == "success"
    assert data["message"] == "Budget created."
    assert data["action"] is None
    assert data["budget"]["category"] == "Gas"
    assert data["budget"]["limit_amount"] == "500.00"
    assert data["budget"]["user_id"] == user_a["id"]

    list_response = client.get("/budgets")
    assert list_response.status_code == 200
    budgets = list_response.json()
    assert len(budgets) == 1
    assert budgets[0]["id"] == data["budget"]["id"]
    assert budgets[0]["limit_amount"] == "500.00"


@patch("app.services.ai_action_service.generate_text")
def test_action_creates_budget_normalizes_category(mock_generate_text, client, user_a):
    mock_generate_text.return_value = AIGenerateTextResponse(
        enabled=True,
        text='{"intent": "create_budget", "category": "  grocery  ", "limit_amount": 350}',
    )

    response = client.post(
        "/ai/action",
        json={"message": "Make me a grocery budget for $350"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["message"] == "Budget created."
    assert data["budget"]["category"] == "Grocery"
    assert data["budget"]["limit_amount"] == "350.00"


@patch("app.services.ai_action_service.generate_text")
def test_action_handles_invalid_budget_amount(mock_generate_text, client, user_a):
    mock_generate_text.return_value = AIGenerateTextResponse(
        enabled=True,
        text='{"intent": "create_budget", "category": "Entertainment", "limit_amount": -120}',
    )

    response = client.post(
        "/ai/action",
        json={"message": "Budget $120 for entertainment"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "parse_error"
    assert data["budget"] is None
    assert client.get("/budgets").json() == []


@patch("app.services.ai_action_service.generate_text")
def test_action_handles_malformed_budget_response(mock_generate_text, client, user_a):
    mock_generate_text.return_value = AIGenerateTextResponse(
        enabled=True,
        text='{"intent": "create_budget", "limit_amount": 500}',
    )

    response = client.post(
        "/ai/action",
        json={"message": "Create a $500 gas budget"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "parse_error"
    assert data["budget"] is None
    assert client.get("/budgets").json() == []


def test_action_budget_requires_authentication(client):
    response = client.post(
        "/ai/action",
        json={"message": "Create a $500 gas budget"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@patch("app.services.ai_action_service.generate_text")
def test_action_parses_unknown_intent(mock_generate_text, client, user_a):
    mock_generate_text.return_value = AIGenerateTextResponse(
        enabled=True,
        text='{"intent": "unknown", "reason": "Message is a general question"}',
    )

    response = client.post(
        "/ai/action",
        json={"message": "How am I doing this month?"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["action"]["intent"] == "unknown"
    assert data["action"]["reason"] == "Message is a general question"


@patch("app.services.ai_action_service.generate_text")
def test_action_maps_unsupported_intent_to_unknown(mock_generate_text, client, user_a):
    mock_generate_text.return_value = AIGenerateTextResponse(
        enabled=True,
        text='{"intent": "delete_transaction", "id": 1}',
    )

    response = client.post(
        "/ai/action",
        json={"message": "Delete my last transaction"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["action"]["intent"] == "unknown"
    assert "Unsupported intent" in data["action"]["reason"]


@patch("app.services.ai_action_service.generate_text")
def test_action_handles_missing_amount(mock_generate_text, client, user_a):
    mock_generate_text.return_value = AIGenerateTextResponse(
        enabled=True,
        text=(
            '{"intent": "create_transaction", "type": "expense", '
            '"category": "Dining", "description": "Dinner", "date": "today"}'
        ),
    )

    response = client.post(
        "/ai/action",
        json={"message": "I spent money on dinner"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "parse_error"
    assert data["transaction"] is None
    assert client.get("/transactions").json()["total_count"] == 0


@patch("app.services.ai_action_service.generate_text")
def test_action_handles_invalid_transaction_type(mock_generate_text, client, user_a):
    mock_generate_text.return_value = AIGenerateTextResponse(
        enabled=True,
        text=(
            '{"intent": "create_transaction", "amount": 42.18, "type": "purchase", '
            '"category": "Dining", "description": "Dinner", "date": "today"}'
        ),
    )

    response = client.post(
        "/ai/action",
        json={"message": "I spent $42.18 on dinner"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "parse_error"
    assert data["transaction"] is None
    assert client.get("/transactions").json()["total_count"] == 0


@patch("app.services.ai_action_service.generate_text")
def test_action_handles_invalid_transaction_date(mock_generate_text, client, user_a):
    mock_generate_text.return_value = AIGenerateTextResponse(
        enabled=True,
        text=(
            '{"intent": "create_transaction", "amount": 42.18, "type": "expense", '
            '"category": "Dining", "description": "Dinner", "date": "yesterday"}'
        ),
    )

    response = client.post(
        "/ai/action",
        json={"message": "I spent $42.18 on dinner yesterday"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "validation_error"
    assert data["transaction"] is None
    assert "invalid" in data["message"].lower()
    assert client.get("/transactions").json()["total_count"] == 0


@patch("app.services.ai_action_service.generate_text")
def test_action_handles_malformed_json(mock_generate_text, client, user_a):
    mock_generate_text.return_value = AIGenerateTextResponse(
        enabled=True,
        text="not valid json",
    )

    response = client.post(
        "/ai/action",
        json={"message": "I spent $45 on dinner"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "parse_error"
    assert data["action"] is None
    assert "parse" in data["message"].lower()


@patch("app.services.ai_action_service.generate_text")
def test_action_handles_invalid_action_shape(mock_generate_text, client, user_a):
    mock_generate_text.return_value = AIGenerateTextResponse(
        enabled=True,
        text='{"intent": "create_transaction", "amount": -5, "type": "expense"}',
    )

    response = client.post(
        "/ai/action",
        json={"message": "I spent -5 on dinner"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "parse_error"
    assert data["action"] is None


@patch("app.services.ai_action_service.generate_text")
def test_action_strips_json_code_fence(mock_generate_text, client, user_a):
    mock_generate_text.return_value = AIGenerateTextResponse(
        enabled=True,
        text=(
            '```json\n{"intent": "create_budget", "category": "Food", '
            '"limit_amount": 300}\n```'
        ),
    )

    response = client.post(
        "/ai/action",
        json={"message": "Budget $300 for food"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["message"] == "Budget created."
    assert data["budget"]["category"] == "Food"
    assert data["budget"]["limit_amount"] == "300.00"


@patch("app.services.ai_action_service.generate_text")
def test_action_gemini_failure_returns_service_unavailable(
    mock_generate_text, client, user_a
):
    mock_generate_text.side_effect = AIServiceError(
        "AI service is temporarily unavailable. Please try again later."
    )

    response = client.post(
        "/ai/action",
        json={"message": "I spent $45 on dinner"},
    )

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "AI service is temporarily unavailable. Please try again later."
    )


@patch("app.services.ai_action_service.generate_text")
def test_action_empty_response_returns_service_unavailable(
    mock_generate_text, client, user_a
):
    mock_generate_text.return_value = AIGenerateTextResponse(enabled=True, text="")

    response = client.post(
        "/ai/action",
        json={"message": "I spent $45 on dinner"},
    )

    assert response.status_code == 503
    assert "empty response" in response.json()["detail"].lower()


def test_parse_action_json_create_transaction():
    action = parse_action_json(
        '{"intent": "create_transaction", "amount": 45.67, "type": "expense", '
        '"category": "Dining", "description": "Dinner", "date": "today"}'
    )

    assert action.intent == "create_transaction"
    assert str(action.amount) == "45.67"
    assert action.type == "expense"
    assert action.category == "Dining"


def test_transaction_create_from_action_uses_existing_validation():
    from app.schemas.ai import CreateTransactionAction

    action = CreateTransactionAction(
        intent="create_transaction",
        amount="10.00",
        type="expense",
        category="food",
        description="Snack",
        date="today",
    )
    transaction_in = transaction_create_from_action(action)

    assert transaction_in.category == "Food"
    assert transaction_in.amount == pytest.approx(action.amount)
    assert transaction_in.transaction_date == datetime.now(UTC).date()


def test_budget_create_from_action_uses_existing_validation():
    from app.schemas.ai import CreateBudgetAction

    action = CreateBudgetAction(
        intent="create_budget",
        category="gas",
        limit_amount="500",
    )
    budget_in = budget_create_from_action(action)

    assert budget_in.category == "Gas"
    assert budget_in.limit_amount == action.limit_amount


def test_parse_action_json_unsupported_intent():
    action = parse_action_json('{"intent": "transfer_funds"}')

    assert action.intent == "unknown"
    assert "Unsupported intent" in action.reason
