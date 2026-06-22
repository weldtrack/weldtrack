from datetime import datetime, timezone
import json

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.user import User
from app.core.config import AUTH_COOKIE_NAME
from app.core.jwt import decode_jwt

"""
Authentication dependencies for routes.
"""


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """
    Dependency to get the current authenticated user from request cookies or header.
    """
    token = request.cookies.get(AUTH_COOKIE_NAME)

    if token is None:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]

    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_jwt(token)
        user_id = int(payload["sub"])
        token_iat = int(payload.get("iat", 0))
    except (KeyError, ValueError, TypeError, json.JSONDecodeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None

    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Logout token revocation validation
    if user.logged_out_at is not None:
        logout_timestamp = int(user.logged_out_at.timestamp())
        if token_iat < logout_timestamp:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked (user logged out)",
                headers={"WWW-Authenticate": "Bearer"},
            )

    # Last active tracking
    try:
        user.last_active = datetime.now(timezone.utc)
        db.add(user)
        db.commit()
        db.refresh(user)
    except Exception:
        db.rollback()
    return user
