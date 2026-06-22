from __future__ import annotations

import secrets

from fastapi import Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    AUTH_COOKIE_NAME,
    AUTH_COOKIE_SAMESITE,
    AUTH_COOKIE_SECURE,
)

from app.core.jwt import create_access_token
from app.models.user import User
from app.schemas.user import AuthResponse, UserRead


def get_user_response(user: User) -> UserRead:
    return UserRead.model_validate(user)


def build_auth_response(user: User) -> AuthResponse:
    return AuthResponse(access_token=create_access_token(user), user=get_user_response(user))


def set_auth_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=AUTH_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=AUTH_COOKIE_SECURE,
        samesite=AUTH_COOKIE_SAMESITE,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


def generate_verification_code() -> str:
    """Generate a cryptographically random 6-digit verification code."""
    return str(secrets.randbelow(1000000)).zfill(6)