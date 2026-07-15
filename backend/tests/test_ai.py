from datetime import UTC, datetime
from unittest.mock import patch

from app.schemas.ai import AIGenerateTextResponse
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
