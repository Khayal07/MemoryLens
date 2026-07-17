"""Shared API dependencies: DB session + current-user resolution from a Bearer
access token."""

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.errors import UnauthorizedError
from app.core.security import decode_token
from app.infra.db import get_db
from app.infra.models import User

_bearer = HTTPBearer(auto_error=False)


def _user_from_credentials(
    creds: HTTPAuthorizationCredentials | None, db: Session
) -> User | None:
    if creds is None:
        return None
    try:
        payload = decode_token(creds.credentials)
    except jwt.PyJWTError:
        raise UnauthorizedError("Invalid or expired token.") from None
    if payload.get("type") != "access":
        raise UnauthorizedError("Invalid token type.")
    user = db.get(User, int(payload["sub"]))
    if user is None:
        raise UnauthorizedError("User no longer exists.")
    return user


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    user = _user_from_credentials(creds, db)
    if user is None:
        raise UnauthorizedError("Authentication required.")
    return user
