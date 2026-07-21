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


def test_dashboard_balance_is_all_time(client, user_a):
    create_transaction(
        client,
        description="Salary",
        amount="1000.00",
        transaction_type="income",
        category="Salary",
        transaction_date=_current_month_date(),
    )
    create_transaction(
        client,
        description="Groceries",
        amount="300.00",
        transaction_type="expense",
        category="Food",
        transaction_date=_current_month_date(),
    )

    response = client.get("/dashboard")

    assert response.status_code == 200
    assert Decimal(response.json()["current_balance"]) == Decimal("700.00")


def test_dashboard_monthly_summary_uses_current_month_only(client, user_a):
    create_transaction(
        client,
        description="Current income",
        amount="1000.00",
        transaction_type="income",
        category="Salary",
        transaction_date=_current_month_date(),
    )
    create_transaction(
        client,
        description="Old income",
        amount="500.00",
        transaction_type="income",
        category="Salary",
        transaction_date=_previous_month_date(),
    )
    create_transaction(
        client,
        description="Current expense",
        amount="100.00",
        transaction_type="expense",
        category="Food",
        transaction_date=_current_month_date(),
    )

    response = client.get("/dashboard")

    assert response.status_code == 200
    summary = response.json()["monthly_summary"]
    assert Decimal(summary["income"]) == Decimal("1000.00")
    assert Decimal(summary["expenses"]) == Decimal("100.00")


def test_dashboard_recent_transactions_limited_to_five(client, user_a):
    for index in range(6):
        create_transaction(
            client,
            description=f"Transaction {index}",
            amount="10.00",
            transaction_date=_current_month_date(day=min(index + 1, 28)),
        )

    response = client.get("/dashboard")

    assert response.status_code == 200
    assert len(response.json()["recent_transactions"]) == 5


def test_dashboard_budget_overview_ignores_previous_month_spending(client, user_a):
    client.post(
        "/budgets",
        json={"category": "Food", "limit_amount": "500.00"},
    )
    create_transaction(
        client,
        amount="400.00",
        category="Food",
        description="Old spending",
        transaction_date=_previous_month_date(),
    )
    create_transaction(
        client,
        amount="50.00",
        category="Food",
        description="Current spending",
        transaction_date=_current_month_date(),
    )

    response = client.get("/dashboard")

    assert response.status_code == 200
    overview = response.json()["budget_overview"]
    assert len(overview) == 1
    assert Decimal(overview[0]["spent"]) == Decimal("50.00")
    assert overview[0]["percentage"] == 10.0


def test_dashboard_budget_overview_limited_to_five_highest_usage(client, user_a):
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
            json={"category": category, "limit_amount": limit_amount},
        )
        create_transaction(
            client,
            description=f"{category} spend",
            amount=spent_amount,
            category=category,
            transaction_date=_current_month_date(),
        )

    response = client.get("/dashboard")

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


def test_dashboard_monthly_trends_reflect_transaction_totals(client, user_a):
    create_transaction(
        client,
        description="Current income",
        amount="200.00",
        transaction_type="income",
        category="Salary",
        transaction_date=_current_month_date(),
    )
    create_transaction(
        client,
        description="Current expense",
        amount="50.00",
        transaction_type="expense",
        category="Food",
        transaction_date=_current_month_date(),
    )
    create_transaction(
        client,
        description="Previous expense",
        amount="80.00",
        transaction_type="expense",
        category="Food",
        transaction_date=_previous_month_date(),
    )

    response = client.get("/dashboard")
    assert response.status_code == 200
    data = response.json()

    current_label = datetime.now(UTC).strftime("%b %Y")
    previous = datetime.now(UTC).date()
    year = previous.year
    month = previous.month - 1
    if month == 0:
        month = 12
        year -= 1
    previous_label = datetime(year, month, 1, tzinfo=UTC).strftime("%b %Y")

    spending_by_month = {
        item["month"]: Decimal(item["total_expenses"])
        for item in data["monthly_spending_trend"]
    }
    comparison_by_month = {
        item["month"]: item for item in data["monthly_comparison_trend"]
    }

    assert spending_by_month[current_label] == Decimal("50.00")
    assert spending_by_month[previous_label] == Decimal("80.00")
    assert comparison_by_month[current_label]["income"] == "200.00"
    assert comparison_by_month[current_label]["expenses"] == "50.00"
    assert comparison_by_month[current_label]["net_savings"] == "150.00"
    assert len(data["monthly_spending_trend"]) == 6
    assert len(data["monthly_comparison_trend"]) == 6


def test_dashboard_response_fields_unchanged(client, user_a):
    create_transaction(
        client,
        amount="25.00",
        category="Food",
        transaction_date=_current_month_date(),
    )

    response = client.get("/dashboard")
    assert response.status_code == 200
    data = response.json()

    assert set(data.keys()) == {
        "current_balance",
        "monthly_summary",
        "recent_transactions",
        "budget_overview",
        "monthly_spending_trend",
        "monthly_comparison_trend",
    }
    assert set(data["monthly_summary"].keys()) == {"income", "expenses"}
    assert isinstance(data["recent_transactions"], list)
    assert isinstance(data["budget_overview"], list)
    assert isinstance(data["monthly_spending_trend"], list)
    assert isinstance(data["monthly_comparison_trend"], list)


def test_dashboard_sql_query_count(client, user_a):
    from sqlalchemy import event

    from app.db.session import engine

    query_count = 0

    def _count_query(*_args, **_kwargs) -> None:
        nonlocal query_count
        query_count += 1

    event.listen(engine, "after_cursor_execute", _count_query)
    try:
        response = client.get("/dashboard")
    finally:
        event.remove(engine, "after_cursor_execute", _count_query)

    assert response.status_code == 200
    assert query_count == 6
