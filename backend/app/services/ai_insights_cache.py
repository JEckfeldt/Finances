"""
In-process cache for AI financial insights keyed by user and data fingerprint.

Stores API responses only; prompts and transaction rows are never cached.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass

from app.schemas.ai import AIInsightsResponse

_lock = threading.Lock()
_cache: dict[int, _CacheEntry] = {}


@dataclass(frozen=True)
class _CacheEntry:
    fingerprint: str
    response: AIInsightsResponse


def get_cached_insights(
    user_id: int, fingerprint: str
) -> AIInsightsResponse | None:
    with _lock:
        entry = _cache.get(user_id)
        if entry is None or entry.fingerprint != fingerprint:
            return None
        return entry.response.model_copy(deep=True)


def set_cached_insights(
    user_id: int, fingerprint: str, response: AIInsightsResponse
) -> None:
    with _lock:
        _cache[user_id] = _CacheEntry(
            fingerprint=fingerprint,
            response=response.model_copy(deep=True),
        )


def clear_ai_insights_cache() -> None:
    """Reset cache (tests and local development)."""
    with _lock:
        _cache.clear()
