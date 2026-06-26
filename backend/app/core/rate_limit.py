"""Fixed-window rate limiting backed by Redis. Fails open: if Redis is unreachable
we allow the request rather than taking the API down. `/search` uses a tighter
limit than auth because it triggers an LLM call."""

import redis
import structlog
from fastapi import Request

from app.core.errors import RateLimitedError
from app.infra.redis import get_redis

log = structlog.get_logger()


def _client_key(request: Request, scope: str) -> str:
    host = request.client.host if request.client else "unknown"
    return f"rl:{scope}:{host}"


def _check(key: str, limit: int, window_seconds: int) -> None:
    try:
        client = get_redis()
        count = client.incr(key)
        if count == 1:
            client.expire(key, window_seconds)
        if count > limit:
            raise RateLimitedError("Too many requests. Please slow down.")
    except redis.RedisError as exc:
        log.warning("rate_limit.redis_unavailable", error=str(exc))  # fail open


def rate_limiter(scope: str, limit: int, window_seconds: int = 60):
    """Build a FastAPI dependency enforcing `limit` requests per window per client."""

    def dependency(request: Request) -> None:
        _check(_client_key(request, scope), limit, window_seconds)

    return dependency
