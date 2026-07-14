"""HttpOnly access-token cookie helpers."""

from fastapi.responses import Response

from app.core.config import settings


def _cookie_options() -> dict[str, bool | str]:
    options: dict[str, bool | str] = {
        "httponly": settings.COOKIE_HTTPONLY,
        "secure": settings.COOKIE_SECURE,
        "samesite": settings.COOKIE_SAMESITE,
        "path": "/",
    }
    if settings.COOKIE_DOMAIN:
        options["domain"] = settings.COOKIE_DOMAIN
    return options


def cookie_defaults() -> dict[str, bool | str]:
    """Return default cookie flags for Set-Cookie responses."""
    return {
        "secure": settings.COOKIE_SECURE,
        "httponly": settings.COOKIE_HTTPONLY,
        "samesite": settings.COOKIE_SAMESITE,
    }


def set_access_token_cookie(response: Response, token: str) -> None:
    """Attach the JWT access token as an HttpOnly cookie."""
    response.set_cookie(
        key=settings.ACCESS_TOKEN_COOKIE_NAME,
        value=token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        **_cookie_options(),
    )


def clear_access_token_cookie(response: Response) -> None:
    """Remove the access-token cookie from the client."""
    delete_kwargs: dict[str, bool | str] = {
        "path": "/",
        "secure": settings.COOKIE_SECURE,
        "httponly": settings.COOKIE_HTTPONLY,
        "samesite": settings.COOKIE_SAMESITE,
    }
    if settings.COOKIE_DOMAIN:
        delete_kwargs["domain"] = settings.COOKIE_DOMAIN
    response.delete_cookie(
        key=settings.ACCESS_TOKEN_COOKIE_NAME,
        **delete_kwargs,
    )
