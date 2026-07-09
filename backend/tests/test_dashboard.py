from datetime import UTC, datetime
from decimal import Decimal

from tests.conftest import auth_headers, create_transaction


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


def test_dashboard_balance_is_all_time(client, user_a):
    _, token = user_a
    create_transaction(
        client,
        token,
        description="Salary",
        amount="1000.00",
        transaction_type="income",
        category="Salary",
        transaction_date=_current_month_date(),
    )
    create_transaction(
        client,
        token,
        description="Groceries",
        amount="300.00",
        transaction_type="expense",
        category="Food",
        transaction_date=_current_month_date(),
    )

    response = client.get("/dashboard", headers=auth_headers(token))

    assert response.status_code == 200
    assert Decimal(response.json()["current_balance"]) == Decimal("700.00")


def test_dashboard_monthly_summary_uses_current_month_only(client, user_a):
    _, token = user_a
    create_transaction(
        client,
        token,
        description="Current income",
        amount="1000.00",
        transaction_type="income",
        category="Salary",
        transaction_date=_current_month_date(),
    )
    create_transaction(
        client,
        token,
        description="Old income",
        amount="500.00",
        transaction_type="income",
        category="Salary",
        transaction_date=_previous_month_date(),
    )
    create_transaction(
        client,
        token,
        description="Current expense",
        amount="100.00",
        transaction_type="expense",
        category="Food",
        transaction_date=_current_month_date(),
    )

    response = client.get("/dashboard", headers=auth_headers(token))

    assert response.status_code == 200
    summary = response.json()["monthly_summary"]
    assert Decimal(summary["income"]) == Decimal("1000.00")
    assert Decimal(summary["expenses"]) == Decimal("100.00")


def test_dashboard_recent_transactions_limited_to_five(client, user_a):
    _, token = user_a

    for index in range(6):
        create_transaction(
            client,
            token,
            description=f"Transaction {index}",
            amount="10.00",
            transaction_date=_current_month_date(day=min(index + 1, 28)),
        )

    response = client.get("/dashboard", headers=auth_headers(token))

    assert response.status_code == 200
    assert len(response.json()["recent_transactions"]) == 5


def test_dashboard_budget_overview_limited_to_five_highest_usage(client, user_a):
    _, token = user_a

    budgets = [
        ("Low", "1000.00", "10.00"),
        ("Medium", "1000.00", "500.00"),
        ("High", "1000.00", "900.00"),
        ("VeryHigh", "1000.00", "950.00"),
        ("Top", "1000.00", "990.00"),
        ("Extra", "1000.00", "100.00"),
    ]

    for category, limit_amount, spent_amount in budgets:
        client.post(
            "/budgets",
            headers=auth_headers(token),
            json={"category": category, "limit_amount": limit_amount},
        )
        create_transaction(
            client,
            token,
            description=f"{category} spend",
            amount=spent_amount,
            category=category,
            transaction_date=_current_month_date(),
        )

    response = client.get("/dashboard", headers=auth_headers(token))

    assert response.status_code == 200
    overview = response.json()["budget_overview"]
    assert len(overview) == 5

    categories = [item["category"] for item in overview]
    assert "Top" in categories
    assert "Veryhigh" in categories
    assert "High" in categories
    assert "Low" not in categories

    percentages = [item["percentage"] for item in overview]
    assert percentages == sorted(percentages, reverse=True)
