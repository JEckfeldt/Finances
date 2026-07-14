from tests.conftest import bearer_headers, create_transaction


def test_create_transaction(client, user_a):
    _, token = user_a

    transaction = create_transaction(client, token, description="Groceries")

    assert transaction["description"] == "Groceries"
    assert transaction["type"] == "expense"
    assert transaction["category"] == "Food"


def test_list_transactions(client, user_a):
    _, token = user_a
    create_transaction(client, token, description="First")
    create_transaction(client, token, description="Second")

    response = client.get("/transactions", headers=bearer_headers(client, token))

    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] == 2
    assert len(data["items"]) == 2


def test_update_transaction(client, user_a):
    _, token = user_a
    transaction = create_transaction(client, token, description="Original")

    response = client.put(
        f"/transactions/{transaction['id']}",
        headers=bearer_headers(client, token),
        json={
            "description": "Updated",
            "amount": "75.00",
            "type": "expense",
            "category": "Food",
            "transaction_date": "2026-07-08",
        },
    )

    assert response.status_code == 200
    assert response.json()["description"] == "Updated"
    assert response.json()["amount"] == "75.00"


def test_delete_transaction(client, user_a):
    _, token = user_a
    transaction = create_transaction(client, token)

    delete_response = client.delete(
        f"/transactions/{transaction['id']}",
        headers=bearer_headers(client, token),
    )
    assert delete_response.status_code == 204

    list_response = client.get("/transactions", headers=bearer_headers(client, token))
    assert list_response.json()["total_count"] == 0


def test_category_normalization(client, user_a):
    _, token = user_a

    transaction = create_transaction(client, token, category="  food  ")

    assert transaction["category"] == "Food"


def test_category_normalization_is_consistent(client, user_a):
    _, token = user_a

    variants = ["food", "Food", " FOOD "]
    categories = []

    for index, category in enumerate(variants):
        transaction = create_transaction(
            client,
            token,
            description=f"Variant {index}",
            category=category,
        )
        categories.append(transaction["category"])

    assert categories == ["Food", "Food", "Food"]


def test_user_cannot_access_other_users_transaction(client, user_a, user_b):
    _, token_a = user_a
    _, token_b = user_b
    transaction = create_transaction(client, token_a, description="Private")

    get_response = client.get("/transactions", headers=bearer_headers(client, token_b))
    assert get_response.status_code == 200
    assert get_response.json()["total_count"] == 0

    update_response = client.put(
        f"/transactions/{transaction['id']}",
        headers=bearer_headers(client, token_b),
        json={
            "description": "Hacked",
            "amount": "1.00",
            "type": "expense",
            "category": "Food",
            "transaction_date": "2026-07-08",
        },
    )
    assert update_response.status_code == 404

    delete_response = client.delete(
        f"/transactions/{transaction['id']}",
        headers=bearer_headers(client, token_b),
    )
    assert delete_response.status_code == 404

    still_there = client.get("/transactions", headers=bearer_headers(client, token_a))
    assert still_there.json()["total_count"] == 1
