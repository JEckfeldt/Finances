"""
Lightweight request and database query timing for performance baselines.

- HTTP: logs method, path, status, wall time (all environments).
- SQL: logs per-query duration and request-level query totals (development only).
"""

from __future__ import annotations

import contextvars
import logging
import time
from typing import Any

from sqlalchemy import event
from sqlalchemy.engine import Engine

from app.core.config import settings

perf_logger = logging.getLogger("app.performance")

_query_stats: contextvars.ContextVar[dict[str, float | int] | None] = contextvars.ContextVar(
    "perf_query_stats",
    default=None,
)

_query_logging_registered = False
_performance_logging_configured = False


def configure_performance_logging() -> None:
    """
    Enable DEBUG output for app.performance in development only.

    Root logging stays at INFO so other loggers are unchanged. Production is not
    affected (this function returns immediately when APP_ENV=production).
    """
    global _performance_logging_configured

    if not settings.is_development:
        return

    if _performance_logging_configured:
        return

    perf_logger.setLevel(logging.DEBUG)

    if not perf_logger.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
        )
        perf_logger.addHandler(handler)

    perf_logger.propagate = False
    _performance_logging_configured = True
    perf_logger.info("Performance DEBUG logging enabled (individual SQL queries)")


def _reset_query_stats() -> None:
    _query_stats.set({"count": 0, "total_ms": 0.0})


def _record_query(duration_ms: float, statement: str) -> None:
    stats = _query_stats.get()
    if stats is None:
        return

    stats["count"] = int(stats["count"]) + 1
    stats["total_ms"] = float(stats["total_ms"]) + duration_ms

    sql_preview = " ".join(statement.split())
    if len(sql_preview) > 240:
        sql_preview = f"{sql_preview[:240]}..."

    perf_logger.debug("SQL %.2fms | %s", duration_ms, sql_preview)


def register_sqlalchemy_query_logging(engine: Engine) -> None:
    """Attach cursor timing listeners to the application engine (development only)."""
    global _query_logging_registered

    if not settings.is_development:
        return

    if _query_logging_registered:
        return

    @event.listens_for(engine, "before_cursor_execute")
    def _before_cursor_execute(
        conn: Any,
        cursor: Any,
        statement: str,
        parameters: Any,
        context: Any,
        executemany: bool,
    ) -> None:
        conn.info.setdefault("_perf_query_start_stack", []).append(time.perf_counter())

    @event.listens_for(engine, "after_cursor_execute")
    def _after_cursor_execute(
        conn: Any,
        cursor: Any,
        statement: str,
        parameters: Any,
        context: Any,
        executemany: bool,
    ) -> None:
        stack: list[float] = conn.info.get("_perf_query_start_stack", [])
        if not stack:
            return

        start = stack.pop()
        duration_ms = (time.perf_counter() - start) * 1000
        _record_query(duration_ms, statement)

    _query_logging_registered = True
    perf_logger.info("SQLAlchemy query timing instrumentation enabled (development)")


class RequestTimingMiddleware:
    """ASGI middleware that logs HTTP request duration."""

    def __init__(self, app: Any) -> None:
        self.app = app

    async def __call__(self, scope: dict[str, Any], receive: Any, send: Any) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        if settings.is_development:
            _reset_query_stats()

        start = time.perf_counter()
        status_code = 500

        async def send_wrapper(message: dict[str, Any]) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        await self.app(scope, receive, send_wrapper)

        duration_ms = (time.perf_counter() - start) * 1000
        method = scope.get("method", "")
        path = scope.get("path", "")

        if settings.is_development:
            stats = _query_stats.get() or {"count": 0, "total_ms": 0.0}
            perf_logger.info(
                "HTTP %s %s %s %.2fms queries=%d db=%.2fms",
                method,
                path,
                status_code,
                duration_ms,
                int(stats["count"]),
                float(stats["total_ms"]),
            )
            _query_stats.set(None)
        else:
            perf_logger.info(
                "HTTP %s %s %s %.2fms",
                method,
                path,
                status_code,
                duration_ms,
            )
