"""Shared test fixtures."""

import pytest

from app.infra import redis as redis_mod


@pytest.fixture(autouse=True)
def _reset_redis_circuit():
    """The Redis circuit breaker is process-global state; a test that simulates a
    Redis failure would otherwise leave the circuit open for later tests. Reset it
    before each test so they stay isolated."""
    redis_mod._down_until = 0.0
    yield
