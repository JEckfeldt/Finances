import logging
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

if os.getenv("APP_ENV", "development").lower() != "production":
    load_dotenv()

logger = logging.getLogger(__name__)

DEFAULT_SECRET_KEY = "change-me-in-production"


class Settings:
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/finance_app",
    )
    SECRET_KEY: str = os.getenv("SECRET_KEY", DEFAULT_SECRET_KEY)
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", str(60 * 24 * 7))
    )
    CORS_ORIGINS: list[str] = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
        if origin.strip()
    ]

    @property
    def is_production(self) -> bool:
        return self.APP_ENV.lower() == "production"

    @property
    def is_development(self) -> bool:
        return not self.is_production


settings = Settings()


def validate_settings() -> None:
    errors: list[str] = []

    if not settings.DATABASE_URL.strip():
        errors.append("DATABASE_URL is required")

    if not settings.SECRET_KEY.strip():
        errors.append("SECRET_KEY is required")

    if settings.is_production:
        if settings.SECRET_KEY == DEFAULT_SECRET_KEY:
            errors.append("SECRET_KEY must be changed from the default in production")
        if len(settings.SECRET_KEY) < 32:
            errors.append("SECRET_KEY must be at least 32 characters in production")

    if not settings.CORS_ORIGINS:
        errors.append("CORS_ORIGINS must include at least one origin")

    if errors:
        for error in errors:
            logger.error("Configuration error: %s", error)
        raise RuntimeError("Configuration validation failed")


def _sanitize_database_url(url: str) -> str:
    parsed = make_url(url)
    host = parsed.host or "unknown-host"
    port = f":{parsed.port}" if parsed.port else ""
    database = parsed.database or "unknown-database"
    username = parsed.username or "unknown-user"
    return f"{parsed.drivername}://{username}:***@{host}{port}/{database}"


def verify_database_connection() -> None:
    sanitized_url = _sanitize_database_url(settings.DATABASE_URL)
    logger.info("Verifying database connection to %s", sanitized_url)
    engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        logger.info("Database connection verified")
    except Exception as exc:
        logger.error(
            "Database connection failed for %s: %s",
            sanitized_url,
            exc,
        )
        raise RuntimeError(
            f"Database connection failed for {sanitized_url}. "
            "Check DATABASE_URL, network access, and database credentials."
        ) from exc
    finally:
        engine.dispose()
