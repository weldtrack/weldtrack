"""
Admin Bootstrap Script

Purpose:
    Creates the initial administrator account in the database.

Rules:
    - ADMIN_EMAIL and ADMIN_PASSWORD must be set in environment variables.
    - Password must be at least 12 characters long.
    - Must contain at least 1 uppercase letter.
    - Must contain at least 1 special character.
    - Must contain at least 1 number.
    - Will only create admin if none exists.

Usage:
    export ADMIN_EMAIL=admin@example.com
    export ADMIN_PASSWORD=StrongPass@123

    python3 -m app.bootstrap.create_initial_admin
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

from sqlalchemy import select

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.core.security import hash_password
from app.db import SessionLocal
from app.models.user import User, UserRole
from app.models.verification_code import EmailVerification


def validate_password(password: str) -> None:
    """
    Ensure password meets security requirements:
    - At least 12 characters
    - At least 1 uppercase letter
    - At least 1 number
    - At least 1 special character
    """

    if len(password) < 12:
        raise ValueError("Password must be at least 12 characters long.")

    if not re.search(r"[A-Z]", password):
        raise ValueError("Password must contain at least one uppercase letter.")

    if not re.search(r"\d", password):
        raise ValueError("Password must contain at least one number.")

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-\\/]", password):
        raise ValueError("Password must contain at least one special character.")


def seed_admin() -> None:
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")

    if not admin_email or not admin_password:
        raise ValueError("ADMIN_EMAIL and ADMIN_PASSWORD are required.")

    # Validate password strength BEFORE touching DB
    validate_password(admin_password)

    db = SessionLocal()

    try:
        existing_admin = db.scalar(
            select(User).where(User.role == UserRole.admin).limit(1)
        )

        if existing_admin:
            print(f"Admin already exists: {existing_admin.email}")
            return

        admin_user = User(
            email=admin_email,
            hashed_password=hash_password(admin_password),
            role=UserRole.admin,
        )

        db.add(admin_user)
        db.flush()

        db.add(
            EmailVerification(
                user_id=admin_user.id,
                is_verified=True,
            )
        )

        db.commit()

        print(f"Successfully created admin account: {admin_email}")

    except Exception as exc:
        db.rollback()
        print(f"Failed to create admin account: {exc}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_admin()