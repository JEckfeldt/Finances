import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings, validate_settings, verify_database_connection
from app.core.performance import (
    RequestTimingMiddleware,
    configure_performance_logging,
    register_sqlalchemy_query_logging,
)
from app.db.base import Base
from app.db.migrate import migrate_foreign_keys, migrate_transactions_table, migrate_users_table
from app.db.session import engine
from app.models import Budget, Transaction, User  # noqa: F401 — register models with metadata

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)


def _initialize_database_schema() -> None:
    if settings.is_production:
        logger.info(
            "Production mode: skipping automatic schema creation and startup migrations"
        )
        logger.info(
            "Ensure the database schema is provisioned before deployment (Alembic recommended)"
        )
        return

    logger.info("Development mode: applying automatic schema setup")
    Base.metadata.create_all(bind=engine)
    migrate_users_table()
    migrate_transactions_table()
    migrate_foreign_keys()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Finance App API (%s)", settings.APP_ENV)
    validate_settings()
    verify_database_connection()
    logger.info(
        "CORS origins: %s | Cookie name: %s | Cookie domain: %s | "
        "Cookie secure: %s | Cookie SameSite: %s",
        ", ".join(settings.CORS_ORIGINS),
        settings.ACCESS_TOKEN_COOKIE_NAME,
        settings.COOKIE_DOMAIN or "(host-only)",
        settings.COOKIE_SECURE,
        settings.COOKIE_SAMESITE,
    )
    _initialize_database_schema()
    configure_performance_logging()
    register_sqlalchemy_query_logging(engine)
    logger.info("Application startup complete")
    yield
    logger.info("Application shutdown")


app = FastAPI(title="Finance App API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestTimingMiddleware)

app.include_router(api_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
