import os
from collections.abc import Generator

import psycopg
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

# Configure test environment before importing application modules.
TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://finance_user:finance_pass@localhost:5432/finance_app_test",
)
os.environ["APP_ENV"] = "development"
os.environ["SECRET_KEY"] = "test-secret-key-with-at-least-32-characters"
os.environ["CORS_ORIGINS"] = "http://localhost:3000"
os.environ["DATABASE_URL"] = TEST_DATABASE_URL

from app.db.base import Base  # noqa: E402
from app.db.session import SessionLocal, engine, get_db  # noqa: E402
from app.main import app  # noqa: E402


def _ensure_test_database() -> None:
    database_url = make_url(os.environ["DATABASE_URL"])
    db_name = database_url.database
    admin_url = database_url.set(database="postgres")
    psycopg_url = admin_url.render_as_string(hide_password=False).replace(
        "postgresql+psycopg://", "postgresql://"
    )

    with psycopg.connect(psycopg_url) as connection:
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s", (db_name,)
            )
            if cursor.fetchone() is None:
                cursor.execute(f'CREATE DATABASE "{db_name}"')


@pytest.fixture(scope="session", autouse=True)
def ensure_test_database() -> None:
    _ensure_test_database()


@pytest.fixture(autouse=True)
def reset_database() -> Generator[None, None, None]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def register_user(
    client: TestClient,
    email: str,
    password: str = "password123",
) -> dict:
    response = client.post(
        "/auth/register",
        json={"email": email, "password": password},
    )
    assert response.status_code == 201
    return response.json()


def login_user(
    client: TestClient,
    email: str,
    password: str = "password123",
) -> str:
    response = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    # login() sets a session cookie; helpers that use Bearer must not inherit it.
    client.cookies.clear()
    return token


def auth_headers(token: str) -> dict[str, str]:
    """Bearer header auth — retained for transition until M17 Iteration 3."""
    return {"Authorization": f"Bearer {token}"}


def bearer_headers(client: TestClient, token: str) -> dict[str, str]:
    """Bearer auth with cookies cleared so cookie-first auth does not override."""
    client.cookies.clear()
    return auth_headers(token)


def create_user_with_token(
    client: TestClient,
    email: str,
    password: str = "password123",
) -> tuple[dict, str]:
    user = register_user(client, email, password)
    token = login_user(client, email, password)
    return user, token


def create_transaction(
    client: TestClient,
    token: str,
    *,
    description: str = "Test transaction",
    amount: str = "100.00",
    transaction_type: str = "expense",
    category: str = "Food",
    transaction_date: str = "2026-07-08",
) -> dict:
    response = client.post(
        "/transactions",
        headers=bearer_headers(client, token),
        json={
            "description": description,
            "amount": amount,
            "type": transaction_type,
            "category": category,
            "transaction_date": transaction_date,
        },
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def user_a(client: TestClient) -> tuple[dict, str]:
    return create_user_with_token(client, "user-a@example.com")


@pytest.fixture
def user_b(client: TestClient) -> tuple[dict, str]:
    return create_user_with_token(client, "user-b@example.com")
