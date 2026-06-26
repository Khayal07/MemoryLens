"""Auth use-cases. Routers handle HTTP + tokens; this layer owns the user rules
and raises typed domain errors."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import ConflictError, UnauthorizedError
from app.core.security import hash_password, verify_password
from app.infra.models import User


def register(db: Session, email: str, password: str) -> User:
    email = email.strip().lower()
    exists = db.execute(select(User.id).where(User.email == email)).scalar_one_or_none()
    if exists is not None:
        raise ConflictError("An account with this email already exists.")
    user = User(email=email, password_hash=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate(db: Session, email: str, password: str) -> User:
    email = email.strip().lower()
    user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if user is None or not verify_password(user.password_hash, password):
        raise UnauthorizedError("Invalid email or password.")
    return user
