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


def estimate_prompt_tokens(char_count: int) -> int:
    """Rough pre-call token estimate (~4 characters per token) for logging."""
    if char_count <= 0:
        return 0
    return max(1, (char_count + 3) // 4)


def log_ai_insights_pipeline(
    *,
    user_id: int,
    financial_data_fetch_ms: float,
    prompt_construction_ms: float,
    transaction_count_total: int,
    transaction_count_current_month: int,
    prompt_chars: int,
    prompt_tokens_estimated: int,
    gemini_request_ms: float | None,
    gemini_input_tokens: int | None,
    gemini_output_tokens: int | None,
    total_request_ms: float,
    ai_enabled: bool,
    cache: str = "miss",
) -> None:
    """Structured timing for POST /ai/insights (no financial payload)."""
    gemini_ms = (
        f"{gemini_request_ms:.2f}"
        if gemini_request_ms is not None
        else "n/a"
    )
    in_tokens = (
        str(gemini_input_tokens) if gemini_input_tokens is not None else "n/a"
    )
    out_tokens = (
        str(gemini_output_tokens) if gemini_output_tokens is not None else "n/a"
    )

    perf_logger.info(
        "AI insights user_id=%s cache=%s fetch=%.2fms prompt_build=%.2fms "
        "transactions_total=%d transactions_current_month=%d "
        "prompt_chars=%d prompt_tokens_est=%d "
        "gemini=%sms gemini_in_tokens=%s gemini_out_tokens=%s "
        "total=%.2fms ai_enabled=%s",
        user_id,
        cache,
        financial_data_fetch_ms,
        prompt_construction_ms,
        transaction_count_total,
        transaction_count_current_month,
        prompt_chars,
        prompt_tokens_estimated,
        gemini_ms,
        in_tokens,
        out_tokens,
        total_request_ms,
        ai_enabled,
    )
