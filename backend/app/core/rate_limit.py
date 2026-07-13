"""Fixed-window rate limiting + a daily quota, backed by Redis. Fails open: if Redis
is unreachable we allow the request rather than taking the API down.

Two identity strategies:
- `rate_limiter` keys off the client IP — used by auth endpoints (no user yet).
- `user_rate_limiter` / `daily_quota` key off the authenticated user id (falling back
  to IP for anonymous callers) so one account can't monopolise an expensive endpoint,
  and so a shared reverse-proxy IP doesn't lump every user into one bucket.

`/search` triggers a paid LLM call, so it carries BOTH a per-minute burst limit and a
per-day quota (a hard ceiling on how much any one user can spend)."""

import datetime as dt

import jwt
import redis
import structlog
from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.errors import RateLimitedError
from app.core.security import decode_token
from app.infra.redis import get_redis, note_redis_failure, redis_unavailable

log = structlog.get_logger()

_bearer = HTTPBearer(auto_error=False)


def _client_ip(request: Request) -> str:
    """The real client IP. Behind our own reverse proxy that's the first hop in
    X-Forwarded-For; for a direct connection it's the socket peer. Only deploy the
    app behind a proxy that overwrites XFF, or a client can spoof its bucket."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _identity(request: Request, creds: HTTPAuthorizationCredentials | None) -> str:
    """`user:<id>` for a valid access token, else `ip:<addr>`. Per-user keying gives
    fair limits that survive a shared proxy IP."""
    if creds is not None:
        try:
            payload = decode_token(creds.credentials)
            if payload.get("type") == "access":
                return f"user:{payload['sub']}"
        except jwt.PyJWTError:
            pass  # fall through to IP for an invalid/expired token
    return f"ip:{_client_ip(request)}"


def _incr_with_ttl(key: str, ttl_seconds: int) -> int:
    """Increment a counter, setting its TTL on first use (fixed window)."""
    client = get_redis()
    count = client.incr(key)
    if count == 1:
        client.expire(key, ttl_seconds)
    return count


def _seconds_until_utc_midnight() -> int:
    now = dt.datetime.now(dt.UTC)
    midnight = (now + dt.timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    return max(1, int((midnight - now).total_seconds()))


def rate_limiter(scope: str, limit: int, window_seconds: int = 60):
    """IP-keyed fixed-window limiter (auth endpoints — there's no user yet)."""

    def dependency(request: Request) -> None:
        if redis_unavailable():
            return  # circuit open — fail open without a slow connect attempt
        key = f"rl:{scope}:ip:{_client_ip(request)}"
        try:
            if _incr_with_ttl(key, window_seconds) > limit:
                raise RateLimitedError("Too many requests. Please slow down.")
        except redis.RedisError as exc:
            note_redis_failure()
            log.warning("rate_limit.redis_unavailable", error=str(exc))  # fail open

    return dependency


def user_rate_limiter(scope: str, limit: int, window_seconds: int = 60):
    """Identity-aware fixed-window limiter: per-user when authenticated, per-IP
    otherwise. Use on expensive endpoints so one account can't burst them."""

    def dependency(
        request: Request,
        creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    ) -> None:
        if redis_unavailable():
            return  # circuit open — fail open without a slow connect attempt
        key = f"rl:{scope}:{_identity(request, creds)}"
        try:
            if _incr_with_ttl(key, window_seconds) > limit:
                raise RateLimitedError("Too many requests. Please slow down.")
        except redis.RedisError as exc:
            note_redis_failure()
            log.warning("rate_limit.redis_unavailable", error=str(exc))  # fail open

    return dependency


def daily_quota(scope: str, limit: int):
    """Per-identity daily cap that resets at UTC midnight — a hard budget ceiling on a
    paid resource, independent of the per-minute pacing."""

    def dependency(
        request: Request,
        creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    ) -> None:
        if redis_unavailable():
            return  # circuit open — fail open without a slow connect attempt
        day = dt.datetime.now(dt.UTC).strftime("%Y-%m-%d")
        key = f"q:{scope}:{_identity(request, creds)}:{day}"
        try:
            if _incr_with_ttl(key, _seconds_until_utc_midnight()) > limit:
                raise RateLimitedError(
                    "Daily search limit reached. Please try again tomorrow."
                )
        except redis.RedisError as exc:
            note_redis_failure()
            log.warning("rate_limit.redis_unavailable", error=str(exc))  # fail open

    return dependency
