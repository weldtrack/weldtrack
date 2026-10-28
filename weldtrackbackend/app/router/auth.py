from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.core.config import AUTH_COOKIE_NAME
from app.core.security import verify_password
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.user import AuthResponse, LoginRequest, UserRead
from app.services.audit_service import log_action
from app.services.auth_service import (
    build_auth_response,
    get_user_by_email,
    get_user_response,
    set_auth_cookie,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=AuthResponse)
def login(
    payload: LoginRequest,
    response: Response,
    request: Request,
    db: Session = Depends(get_db),
) -> AuthResponse:
    user = get_user_by_email(db, payload.email)
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.is_banned:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are banned from logging in. Please contact an administrator.",
        )

    try:
        user.last_active = datetime.now(timezone.utc)
        db.add(user)
        db.commit()
        db.refresh(user)
    except Exception:
        db.rollback()

    auth_response = build_auth_response(user)
    set_auth_cookie(response, auth_response.access_token)

    try:
        log_action(
            db,
            action="AUTH_LOGIN",
            description=f"User {user.full_name or user.email} logged in",
            user=user,
            properties={"email": user.email, "role": user.role.value},
            request=request,
        )
    except Exception:
        pass

    return auth_response


@router.post("/logout")
def logout(
    response: Response,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, bool | str]:
    """Clear the auth cookie and invalidate the token."""
    try:
        current_user.logged_out_at = datetime.now(timezone.utc)
        db.add(current_user)
        db.commit()
        db.refresh(current_user)

        log_action(
            db,
            action="AUTH_LOGOUT",
            description=f"User {current_user.full_name or current_user.email} logged out",
            user=current_user,
            request=request,
        )
    except Exception:
        db.rollback()

    response.delete_cookie(key=AUTH_COOKIE_NAME, path="/")
    return {"success": True, "message": "Logged out successfully"}


@router.get("/me", response_model=UserRead)
def read_current_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserRead:
    return get_user_response(current_user)
