from __future__ import annotations

import os
from sqlalchemy import select

from app.db import SessionLocal
from app.models.user import User, UserRole
from app.models.verification_code import EmailVerification
from app.middleware.auth_middleware import hash_password


def create_initial_admin() -> None:
    """Create an initial admin user only when there are no users in the database.

    Safety rules:
    - Requires both `ADMIN_EMAIL` and `ADMIN_PASSWORD` to be set in the environment.
    - Will only create an admin if there are zero users (one-time bootstrap).
    - If users exist but no admin exists, it will not auto-create an admin.
    """
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

    if not ADMIN_EMAIL or not ADMIN_PASSWORD:
        # nothing to do — admin credentials not provided
        return

    db = SessionLocal()
    try:
        # If any admin exists, do nothing
        admin_exists = db.scalar(select(User).where(User.role == UserRole.admin).limit(1))
        if admin_exists:
            return

        # If any user exists (but no admin), do NOT auto-create admin — safety measure
        any_user = db.scalar(select(User).limit(1))
        if any_user:
            print("Users exist but no admin found; skipping automatic admin bootstrap.")
            return

        # No users at all: safe to create initial admin
        admin = User(
            email=ADMIN_EMAIL,
            hashed_password=hash_password(ADMIN_PASSWORD),
            role=UserRole.admin,
        )
        db.add(admin)
        db.flush()

        ev = EmailVerification(user_id=admin.id, is_verified=True)
        db.add(ev)
        db.commit()
        print("Initial admin account created.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
