from sqlalchemy import select

from app.core.auth import verify_password
from app.models.user import User
from tests.conftest import auth_headers, register_user


def test_register_success(client):
    response = client.post(
        "/auth/register",
        json={"email": "new-user@example.com", "password": "password123"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "new-user@example.com"
    assert "id" in data
    assert "created_at" in data
    assert "password" not in data
    assert "hashed_password" not in data


def test_register_duplicate_email_rejected(client):
    register_user(client, "duplicate@example.com")

    response = client.post(
        "/auth/register",
        json={"email": "duplicate@example.com", "password": "password123"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


def test_register_stores_hashed_password(client, db_session):
    register_user(client, "hashed@example.com", "password123")

    user = db_session.scalar(
        select(User).where(User.email == "hashed@example.com")
    )
    assert user is not None
    assert user.hashed_password != "password123"
    assert verify_password("password123", user.hashed_password)


def test_login_success_returns_token(client):
    register_user(client, "login@example.com")

    response = client.post(
        "/auth/login",
        json={"email": "login@example.com", "password": "password123"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["access_token"]
    assert data["token_type"] == "bearer"


def test_login_invalid_password_rejected(client):
    register_user(client, "bad-password@example.com")

    response = client.post(
        "/auth/login",
        json={"email": "bad-password@example.com", "password": "wrong-password"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


def test_login_unknown_email_rejected(client):
    response = client.post(
        "/auth/login",
        json={"email": "missing@example.com", "password": "password123"},
    )

    assert response.status_code == 401


def test_protected_route_requires_authentication(client):
    response = client.get("/transactions")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_protected_route_accepts_valid_jwt(client, user_a):
    _, token = user_a

    response = client.get("/auth/me", headers=auth_headers(token))

    assert response.status_code == 200
    assert response.json()["email"] == "user-a@example.com"
