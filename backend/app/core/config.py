import logging
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

if os.getenv("APP_ENV", "development").lower() != "production":
    load_dotenv()

logger = logging.getLogger(__name__)

DEFAULT_SECRET_KEY = "change-me-in-production"
DEFAULT_CORS_ORIGINS = "http://localhost:3000"
VALID_COOKIE_SAMESITE_VALUES = {"lax", "strict", "none"}


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _default_cookie_secure() -> bool:
    return os.getenv("APP_ENV", "development").lower() == "production"


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
    ACCESS_TOKEN_COOKIE_NAME: str = os.getenv(
        "ACCESS_TOKEN_COOKIE_NAME", "access_token"
    ).strip()
    CORS_ORIGINS: list[str] = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", DEFAULT_CORS_ORIGINS).split(",")
        if origin.strip()
    ]
    COOKIE_SECURE: bool = _env_bool("COOKIE_SECURE", _default_cookie_secure())
    COOKIE_SAMESITE: str = os.getenv("COOKIE_SAMESITE", "lax").strip().lower()
    COOKIE_HTTPONLY: bool = _env_bool("COOKIE_HTTPONLY", True)
    COOKIE_DOMAIN: str = os.getenv("COOKIE_DOMAIN", "").strip()

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

    if settings.COOKIE_SAMESITE not in VALID_COOKIE_SAMESITE_VALUES:
        errors.append(
            "COOKIE_SAMESITE must be one of: lax, strict, none"
        )

    if not settings.ACCESS_TOKEN_COOKIE_NAME:
        errors.append("ACCESS_TOKEN_COOKIE_NAME must not be empty")

    if settings.COOKIE_SAMESITE == "none" and not settings.COOKIE_SECURE:
        errors.append("COOKIE_SECURE must be true when COOKIE_SAMESITE is none")

    if settings.COOKIE_DOMAIN:
        domain = settings.COOKIE_DOMAIN
        if domain.startswith("."):
            domain = domain[1:]
        if not domain or "." not in domain:
            errors.append(
                "COOKIE_DOMAIN must be a valid domain (e.g. .example.com)"
            )

    if settings.is_production:
        for origin in settings.CORS_ORIGINS:
            if not origin.startswith("https://"):
                errors.append(
                    f"CORS_ORIGINS must use HTTPS in production (got: {origin})"
                )

        if not settings.COOKIE_SECURE:
            errors.append("COOKIE_SECURE must be true in production")

        if not settings.COOKIE_DOMAIN:
            errors.append(
                "COOKIE_DOMAIN is required in production for cross-subdomain cookies"
            )

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
