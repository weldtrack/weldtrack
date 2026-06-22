from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.core.security import hash_password
from app.dependencies.auth import get_current_user
from app.models.user import User, UserRole
from app.models.verification_code import EmailVerification
from app.schemas.user import UserRead
from app.services.auth_service import get_user_by_email, get_user_response

router = APIRouter(prefix="/auth", tags=["admin"])


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requires admin privileges",
        )
    return current_user


def is_user_online(user: User) -> bool:
    """User is considered online if last_active is within the last 30 seconds."""
    if user.last_active is None:
        return False
    return user.last_active >= datetime.now(timezone.utc) - timedelta(seconds=30)


# ── Staff ─────────────────────────────────────────────────────────────────────

@router.get("/staff", response_model=list[UserRead])
def list_staff_users(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[UserRead]:
    users = db.scalars(
        select(User).where(User.role == UserRole.staff).order_by(User.id)
    ).all()
    return [get_user_response(u) for u in users]


@router.post("/admin/create-staff")
def admin_create_staff(
    payload: dict,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Admin-only: create a staff account without requiring email verification."""
    email = payload.get("email")
    password = payload.get("password")

    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required",
        )
    if len(password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long",
        )

    if get_user_by_email(db, email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered",
        )

    user = User(email=email, hashed_password=hash_password(password), role=UserRole.staff)
    db.add(user)
    db.flush()

    db.add(EmailVerification(user_id=user.id, is_verified=True))
    db.commit()
    db.refresh(user)

    return {"success": True, "user": get_user_response(user)}


@router.delete("/staff/{staff_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_staff(
    staff_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Admin-only: delete a staff member."""
    staff_user = db.get(User, staff_id)
    if not staff_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staff member not found")
    if staff_user.role != UserRole.staff:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only delete staff members",
        )

    db.delete(staff_user)
    db.commit()


# ── Users ─────────────────────────────────────────────────────────────────────

@router.get("/admin/users", response_model=list[UserRead])
def admin_get_users(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[UserRead]:
    """Admin-only: get all non-admin users (customers and staff)."""
    users = db.scalars(
        select(User)
        .where(User.role != UserRole.admin)
        .order_by(User.last_active.desc(), User.id.desc())
    ).all()

    for user in users:
        user.is_online = is_user_online(user)

    return [get_user_response(u) for u in users]


@router.get("/admin/online", response_model=list[UserRead])
def admin_get_online_users(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[UserRead]:
    """Admin-only: get users active within the last 30 seconds."""
    thirty_seconds_ago = datetime.now(timezone.utc) - timedelta(seconds=30)

    users = db.scalars(
        select(User)
        .where(User.role != UserRole.admin)
        .where(User.last_active.isnot(None))
        .where(User.last_active >= thirty_seconds_ago)
        .order_by(User.last_active.desc(), User.id.desc())
    ).all()

    for user in users:
        user.is_online = True

    return [get_user_response(u) for u in users]


# ── Ban / Unban ───────────────────────────────────────────────────────────────

@router.post("/admin/ban/{user_id}")
def admin_ban_user(
    user_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, bool | str]:
    """Admin-only: ban a user."""
    if user_id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot ban yourself",
        )

    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.role == UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot ban admin users",
        )

    try:
        user.is_banned = True
        db.add(user)
        db.commit()
        db.refresh(user)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to ban user",
        )

    return {"success": True, "message": f"User {user.email} has been banned"}


@router.post("/admin/unban/{user_id}")
def admin_unban_user(
    user_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, bool | str]:
    """Admin-only: unban a user."""
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.role == UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot unban admin users",
        )

    try:
        user.is_banned = False
        db.add(user)
        db.commit()
        db.refresh(user)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to unban user",
        )

    return {"success": True, "message": f"User {user.email} has been unbanned"}