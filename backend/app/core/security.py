"""Password hashing (Argon2) + JWT issuance/verification. Argon2 is memory-hard
and the current OWASP-preferred default over bcrypt. Tokens are stateless; the
refresh token is distinguished by a `type` claim."""

from datetime import UTC, datetime, timedelta

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from app.core.config import get_settings

_ph = PasswordHasher()
_ALGO = "HS256"


def hash_password(password: str) -> str:
    return _ph.hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    try:
        return _ph.verify(password_hash, password)
    except (VerifyMismatchError, ValueError):
        return False


def _create_token(subject: str, token_type: str, ttl: timedelta) -> str:
    settings = get_settings()
    now = datetime.now(UTC)
    payload = {"sub": subject, "type": token_type, "iat": now, "exp": now + ttl}
    return jwt.encode(payload, settings.jwt_secret, algorithm=_ALGO)


def create_access_token(user_id: int) -> str:
    settings = get_settings()
    return _create_token(str(user_id), "access", timedelta(minutes=settings.jwt_access_ttl_min))


def create_refresh_token(user_id: int) -> str:
    settings = get_settings()
    return _create_token(str(user_id), "refresh", timedelta(days=settings.jwt_refresh_ttl_days))


def decode_token(token: str) -> dict:
    """Decode + verify a token. Raises jwt.PyJWTError on any problem."""
    settings = get_settings()
    return jwt.decode(token, settings.jwt_secret, algorithms=[_ALGO])
