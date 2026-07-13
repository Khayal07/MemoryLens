"""Redis client (cache + rate limiting). Single pooled client per process.

A DOWN or misconfigured Redis must never slow the app down. Two guards:
- short socket timeouts so a connect/read against an unreachable host fails fast;
- a process-level circuit breaker so that once an operation fails, callers skip
  Redis entirely for a cooldown instead of each paying a fresh timeout (a DNS
  failure in particular is ~4s and isn't covered by socket_connect_timeout, and a
  single search does several Redis ops — those stack into ~minute-long requests)."""

import time
from functools import lru_cache

import redis

from app.core.config import get_settings

_COOLDOWN_SECONDS = 30.0
_down_until = 0.0


@lru_cache
def get_redis() -> redis.Redis:
    return redis.Redis.from_url(
        get_settings().redis_url,
        decode_responses=True,
        socket_connect_timeout=0.5,
        socket_timeout=0.5,
        retry_on_timeout=False,
    )


def redis_unavailable() -> bool:
    """True while Redis is in a failure cooldown — callers should skip it and fail
    open rather than pay another slow connect/DNS timeout on every operation."""
    return time.monotonic() < _down_until


def note_redis_failure() -> None:
    """Open the circuit for a cooldown after a Redis operation fails."""
    global _down_until
    _down_until = time.monotonic() + _COOLDOWN_SECONDS
