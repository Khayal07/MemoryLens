"""Config validation: the JWT secret must be strong in production."""

import pytest

from app.core.config import _INSECURE_JWT_DEFAULT, Settings


def test_dev_allows_default_secret():
    s = Settings(env="development", jwt_secret=_INSECURE_JWT_DEFAULT)
    assert s.jwt_secret == _INSECURE_JWT_DEFAULT
    assert s.is_production is False


def test_prod_rejects_default_secret():
    with pytest.raises(ValueError, match="JWT_SECRET"):
        Settings(env="production", jwt_secret=_INSECURE_JWT_DEFAULT)


def test_prod_rejects_empty_secret():
    with pytest.raises(ValueError, match="JWT_SECRET"):
        Settings(env="production", jwt_secret="")


def test_prod_accepts_strong_secret():
    s = Settings(env="production", jwt_secret="a" * 64)
    assert s.is_production is True
    assert s.jwt_secret == "a" * 64


def test_search_cost_controls_have_defaults():
    s = Settings(env="development")
    assert s.search_rate_per_min == 10
    assert s.search_daily_quota == 50
