from datetime import UTC, datetime
from decimal import Decimal

from tests.conftest import create_transaction


def _current_month_date(day: int = 8) -> str:
    today = datetime.now(UTC).date()
    return f"{today.year}-{today.month:02d}-{day:02d}"


def _previous_month_date() -> str:
    today = datetime.now(UTC).date()
    year = today.year
    month = today.month - 1
    if month == 0:
        month = 12
        year -= 1
    return f"{year}-{month:02d}-15"


def _next_month_date() -> str:
    today = datetime.now(UTC).date()
    year = today.year
    month = today.month + 1
    if month > 12:
        month = 1
        year += 1
    return f"{year}-{month:02d}-10"


def test_create_budget(client, user_a):
    response = client.post(
        "/budgets",
        json={"category": "Food", "limit_amount": "500.00"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["category"] == "Food"
    assert data["limit_amount"] == "500.00"


def test_list_budgets(client, user_a):
    client.post(
        "/budgets",
        json={"category": "Food", "limit_amount": "500.00"},
    )

    response = client.get("/budgets")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_update_budget(client, user_a):
    created = client.post(
        "/budgets",
        json={"category": "Food", "limit_amount": "500.00"},
    ).json()

    response = client.put(
        f"/budgets/{created['id']}",
        json={"category": "Groceries", "limit_amount": "600.00"},
    )

    assert response.status_code == 200
    assert response.json()["category"] == "Groceries"
    assert response.json()["limit_amount"] == "600.00"


def test_delete_budget(client, user_a):
    created = client.post(
        "/budgets",
        json={"category": "Food", "limit_amount": "500.00"},
    ).json()

    delete_response = client.delete(f"/budgets/{created['id']}")
    assert delete_response.status_code == 204

    list_response = client.get("/budgets")
    assert list_response.json() == []


def test_budget_progress_case_insensitive(client, user_a):
    client.post(
        "/budgets",
        json={"category": "Food", "limit_amount": "500.00"},
    )

    create_transaction(
        client, amount="100.00", category="food", description="A",
        transaction_date=_current_month_date(),
    )
    create_transaction(
        client, amount="50.00", category="FOOD", description="B",
        transaction_date=_current_month_date(day=9),
    )
    create_transaction(
        client, amount="25.00", category=" Food ", description="C",
        transaction_date=_current_month_date(day=10),
    )

    response = client.get("/budgets/progress")

    assert response.status_code == 200
    progress = response.json()[0]
    assert progress["category"] == "Food"
    assert Decimal(progress["spent"]) == Decimal("175.00")
    assert Decimal(progress["remaining"]) == Decimal("325.00")


def test_budget_progress_uses_current_month_expenses_only(client, user_a):
    client.post(
        "/budgets",
        json={"category": "Food", "limit_amount": "500.00"},
    )

    create_transaction(
        client,
        amount="100.00",
        category="Food",
        description="Current month",
        transaction_date=_current_month_date(),
    )
    create_transaction(
        client,
        amount="200.00",
        category="Food",
        description="Previous month",
        transaction_date=_previous_month_date(),
    )
    create_transaction(
        client,
        amount="150.00",
        category="Food",
        description="Future month",
        transaction_date=_next_month_date(),
    )
    create_transaction(
        client,
        amount="75.00",
        category="Food",
        description="Current month income",
        transaction_type="income",
        transaction_date=_current_month_date(day=11),
    )

    response = client.get("/budgets/progress")

    assert response.status_code == 200
    progress = response.json()[0]
    assert progress["category"] == "Food"
    assert Decimal(progress["spent"]) == Decimal("100.00")
    assert Decimal(progress["remaining"]) == Decimal("400.00")
