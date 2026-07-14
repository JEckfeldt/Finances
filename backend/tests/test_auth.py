from sqlalchemy import select

from app.core.auth import verify_password
from app.core.config import settings
from app.models.user import User
from tests.conftest import register_user


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


def test_login_success_returns_user(client):
    register_user(client, "login@example.com")

    response = client.post(
        "/auth/login",
        json={"email": "login@example.com", "password": "password123"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "login@example.com"
    assert "id" in data
    assert "created_at" in data
    assert "access_token" not in data
    assert "token_type" not in data


def test_login_sets_httponly_access_token_cookie(client):
    register_user(client, "cookie-login@example.com")

    response = client.post(
        "/auth/login",
        json={"email": "cookie-login@example.com", "password": "password123"},
    )

    assert response.status_code == 200
    set_cookie = response.headers.get("set-cookie", "")
    assert f"{settings.ACCESS_TOKEN_COOKIE_NAME}=" in set_cookie
    assert "httponly" in set_cookie.lower()
    assert "path=/" in set_cookie.lower()


def test_protected_route_accepts_cookie_auth(client):
    register_user(client, "cookie-auth@example.com")
    login_response = client.post(
        "/auth/login",
        json={"email": "cookie-auth@example.com", "password": "password123"},
    )
    assert login_response.status_code == 200

    response = client.get("/auth/me")

    assert response.status_code == 200
    assert response.json()["email"] == "cookie-auth@example.com"


def test_logout_clears_authentication_cookie(client):
    register_user(client, "logout@example.com")
    login_response = client.post(
        "/auth/login",
        json={"email": "logout@example.com", "password": "password123"},
    )
    assert login_response.status_code == 200
    assert client.get("/auth/me").status_code == 200

    logout_response = client.post("/auth/logout")

    assert logout_response.status_code == 204
    assert client.get("/auth/me").status_code == 401


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


def test_bearer_token_is_not_accepted(client, user_a):
    client.cookies.clear()
    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_protected_route_accepts_cookie_session(client, user_a):
    response = client.get("/auth/me")

    assert response.status_code == 200
    assert response.json()["email"] == user_a["email"]
