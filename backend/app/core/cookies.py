"""Cookie configuration helpers for future httpOnly authentication."""

from app.core.config import settings


def cookie_defaults() -> dict[str, bool | str]:
    """Return default cookie flags for future Set-Cookie responses."""
    return {
        "secure": settings.COOKIE_SECURE,
        "httponly": settings.COOKIE_HTTPONLY,
        "samesite": settings.COOKIE_SAMESITE,
    }
