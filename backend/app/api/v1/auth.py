"""Auth routes: register, login, refresh, me."""

import jwt
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.errors import UnauthorizedError
from app.core.rate_limit import rate_limiter
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.infra.db import get_db
from app.infra.models import User
from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserOut,
)
from app.services import auth_service

router = APIRouter(dependencies=[Depends(rate_limiter("auth", limit=20))])


def _tokens(user_id: int) -> TokenResponse:
    return TokenResponse(
        access_token=create_access_token(user_id),
        refresh_token=create_refresh_token(user_id),
    )


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(body: RegisterRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = auth_service.register(db, body.email, body.password)
    return _tokens(user.id)


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = auth_service.authenticate(db, body.email, body.password)
    return _tokens(user.id)


@router.post("/refresh", response_model=TokenResponse)
def refresh(body: RefreshRequest, db: Session = Depends(get_db)) -> TokenResponse:
    try:
        payload = decode_token(body.refresh_token)
    except jwt.PyJWTError:
        raise UnauthorizedError("Invalid or expired refresh token.") from None
    if payload.get("type") != "refresh":
        raise UnauthorizedError("Not a refresh token.")
    return _tokens(int(payload["sub"]))


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)) -> UserOut:
    return UserOut(id=user.id, email=user.email)
