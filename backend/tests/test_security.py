"""Unit tests for password hashing + JWT (no DB, no network)."""

import jwt
import pytest

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_hash_is_not_plaintext_and_verifies() -> None:
    h = hash_password("correct horse battery staple")
    assert h != "correct horse battery staple"
    assert verify_password(h, "correct horse battery staple")


def test_wrong_password_fails() -> None:
    h = hash_password("right-password")
    assert not verify_password(h, "wrong-password")


def test_access_token_roundtrip() -> None:
    token = create_access_token(42)
    payload = decode_token(token)
    assert payload["sub"] == "42"
    assert payload["type"] == "access"


def test_refresh_token_type() -> None:
    payload = decode_token(create_refresh_token(7))
    assert payload["type"] == "refresh"
    assert payload["sub"] == "7"


def test_tampered_token_rejected() -> None:
    token = create_access_token(1)
    with pytest.raises(jwt.PyJWTError):
        decode_token(token + "tamper")
