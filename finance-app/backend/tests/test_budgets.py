from decimal import Decimal

from tests.conftest import auth_headers, create_transaction


def test_create_budget(client, user_a):
    _, token = user_a

    response = client.post(
        "/budgets",
        headers=auth_headers(token),
        json={"category": "Food", "limit_amount": "500.00"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["category"] == "Food"
    assert data["limit_amount"] == "500.00"


def test_list_budgets(client, user_a):
    _, token = user_a
    client.post(
        "/budgets",
        headers=auth_headers(token),
        json={"category": "Food", "limit_amount": "500.00"},
    )

    response = client.get("/budgets", headers=auth_headers(token))

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_update_budget(client, user_a):
    _, token = user_a
    created = client.post(
        "/budgets",
        headers=auth_headers(token),
        json={"category": "Food", "limit_amount": "500.00"},
    ).json()

    response = client.put(
        f"/budgets/{created['id']}",
        headers=auth_headers(token),
        json={"category": "Groceries", "limit_amount": "600.00"},
    )

    assert response.status_code == 200
    assert response.json()["category"] == "Groceries"
    assert response.json()["limit_amount"] == "600.00"


def test_delete_budget(client, user_a):
    _, token = user_a
    created = client.post(
        "/budgets",
        headers=auth_headers(token),
        json={"category": "Food", "limit_amount": "500.00"},
    ).json()

    delete_response = client.delete(
        f"/budgets/{created['id']}",
        headers=auth_headers(token),
    )
    assert delete_response.status_code == 204

    list_response = client.get("/budgets", headers=auth_headers(token))
    assert list_response.json() == []


def test_budget_progress_case_insensitive(client, user_a):
    _, token = user_a
    client.post(
        "/budgets",
        headers=auth_headers(token),
        json={"category": "Food", "limit_amount": "500.00"},
    )

    create_transaction(
        client, token, amount="100.00", category="food", description="A"
    )
    create_transaction(
        client, token, amount="50.00", category="FOOD", description="B"
    )
    create_transaction(
        client, token, amount="25.00", category=" Food ", description="C"
    )

    response = client.get("/budgets/progress", headers=auth_headers(token))

    assert response.status_code == 200
    progress = response.json()[0]
    assert progress["category"] == "Food"
    assert Decimal(progress["spent"]) == Decimal("175.00")
    assert Decimal(progress["remaining"]) == Decimal("325.00")
