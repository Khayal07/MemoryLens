"""Unit tests for the identity resolution + limiter/quota dependencies.

Redis is faked so the tests are network-free and deterministic."""

import types

import pytest
import redis
from fastapi.security import HTTPAuthorizationCredentials
from starlette.datastructures import Headers
from starlette.requests import Request

from app.core import rate_limit
from app.core.errors import RateLimitedError
from app.core.security import create_access_token, create_refresh_token


def _request(headers: dict | None = None, client_host: str | None = "1.2.3.4") -> Request:
    raw = [(k.lower().encode(), v.encode()) for k, v in (headers or {}).items()]
    scope = {
        "type": "http",
        "method": "POST",
        "path": "/api/v1/search",
        "headers": raw,
        "client": (client_host, 12345) if client_host else None,
    }
    return Request(scope)


class _FakeRedis:
    """Minimal INCR/EXPIRE counter; raise_on set makes calls fail (fail-open test)."""

    def __init__(self, raise_error: bool = False) -> None:
        self.counts: dict[str, int] = {}
        self.expiries: dict[str, int] = {}
        self.raise_error = raise_error

    def incr(self, key: str) -> int:
        if self.raise_error:
            raise redis.RedisError("down")
        self.counts[key] = self.counts.get(key, 0) + 1
        return self.counts[key]

    def expire(self, key: str, ttl: int) -> None:
        self.expiries[key] = ttl


@pytest.fixture
def fake_redis(monkeypatch):
    fake = _FakeRedis()
    monkeypatch.setattr(rate_limit, "get_redis", lambda: fake)
    return fake


# --- identity resolution -----------------------------------------------------------


class TestIdentity:
    def test_valid_access_token_keys_by_user(self):
        token = create_access_token(42)
        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        assert rate_limit._identity(_request(), creds) == "user:42"

    def test_no_token_falls_back_to_ip(self):
        assert rate_limit._identity(_request(), None) == "ip:1.2.3.4"

    def test_refresh_token_is_not_accepted_as_identity(self):
        # Only an access token identifies a user; a refresh token falls back to IP.
        token = create_refresh_token(7)
        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        assert rate_limit._identity(_request(), creds) == "ip:1.2.3.4"

    def test_garbage_token_falls_back_to_ip(self):
        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="not.a.jwt")
        assert rate_limit._identity(_request(), creds) == "ip:1.2.3.4"


class TestClientIp:
    def test_prefers_first_forwarded_hop(self):
        req = _request({"x-forwarded-for": "9.9.9.9, 10.0.0.1"}, client_host="10.0.0.1")
        assert rate_limit._client_ip(req) == "9.9.9.9"

    def test_falls_back_to_socket_peer(self):
        assert rate_limit._client_ip(_request()) == "1.2.3.4"

    def test_unknown_when_no_client(self):
        assert rate_limit._client_ip(_request(client_host=None)) == "unknown"


# --- limiters ----------------------------------------------------------------------


class TestUserRateLimiter:
    def test_allows_up_to_limit_then_blocks(self, fake_redis):
        dep = rate_limit.user_rate_limiter("search", limit=2)
        req = _request()
        dep(req, None)  # 1
        dep(req, None)  # 2
        with pytest.raises(RateLimitedError):
            dep(req, None)  # 3 → over

    def test_separate_users_have_separate_buckets(self, fake_redis):
        dep = rate_limit.user_rate_limiter("search", limit=1)
        a = HTTPAuthorizationCredentials(scheme="Bearer", credentials=create_access_token(1))
        b = HTTPAuthorizationCredentials(scheme="Bearer", credentials=create_access_token(2))
        dep(_request(), a)  # user 1, first — ok
        dep(_request(), b)  # user 2, first — ok (independent)
        with pytest.raises(RateLimitedError):
            dep(_request(), a)  # user 1, second — over

    def test_first_call_sets_ttl(self, fake_redis):
        rate_limit.user_rate_limiter("search", limit=5)(_request(), None)
        assert any(k.startswith("rl:search:") for k in fake_redis.expiries)

    def test_fails_open_when_redis_down(self, monkeypatch):
        monkeypatch.setattr(rate_limit, "get_redis", lambda: _FakeRedis(raise_error=True))
        # Should NOT raise even far past any limit — availability over strictness.
        rate_limit.user_rate_limiter("search", limit=1)(_request(), None)


class TestDailyQuota:
    def test_blocks_past_daily_cap(self, fake_redis):
        dep = rate_limit.daily_quota("search", limit=3)
        req = _request()
        for _ in range(3):
            dep(req, None)
        with pytest.raises(RateLimitedError):
            dep(req, None)

    def test_quota_key_is_day_scoped(self, fake_redis):
        rate_limit.daily_quota("search", limit=10)(_request(), None)
        assert any(k.startswith("q:search:ip:1.2.3.4:") for k in fake_redis.counts)

    def test_fails_open_when_redis_down(self, monkeypatch):
        monkeypatch.setattr(rate_limit, "get_redis", lambda: _FakeRedis(raise_error=True))
        rate_limit.daily_quota("search", limit=1)(_request(), None)


def test_seconds_until_midnight_is_positive_and_within_a_day():
    secs = rate_limit._seconds_until_utc_midnight()
    assert 0 < secs <= 86400


# Keep the module importable surface stable for callers.
def test_public_dependencies_are_callables():
    assert isinstance(rate_limit.rate_limiter("x", 1), types.FunctionType)
    assert isinstance(rate_limit.user_rate_limiter("x", 1), types.FunctionType)
    assert isinstance(rate_limit.daily_quota("x", 1), types.FunctionType)
