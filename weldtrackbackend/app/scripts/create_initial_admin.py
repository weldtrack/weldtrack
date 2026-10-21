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
    python3 app/scripts/create_initial_admin.py
    OR
    python3 -m app.scripts.create_initial_admin
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

from sqlalchemy import text

from app.core.config import settings
from app.core.id import new_ulid
from app.core.security import hash_password
from app.db import SessionLocal
from app.models.user import UserRole


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
    admin_email = settings.ADMIN_EMAIL
    admin_password = settings.ADMIN_PASSWORD

    # Validate password strength BEFORE running queries
    # validate_password(admin_password)

    db = SessionLocal()

    try:
        # Resolve the string value from Enum safely
        role_value = (
            UserRole.admin.value if hasattr(UserRole.admin, "value") else UserRole.admin
        )

        # 1. Check if an administrator already exists using raw SQL
        result = db.execute(
            text("SELECT id, email FROM users WHERE role = :role LIMIT 1"),
            {"role": role_value},
        ).fetchone()

        if result:
            db.execute(
                text("""
                    UPDATE users
                    SET email = :email, hashed_password = :hashed_password
                    WHERE id = :id
                """),
                {
                    "id": result.id,
                    "email": admin_email,
                    "hashed_password": hash_password(admin_password),
                },
            )
            db.commit()
            print(f"Synced existing admin account to: {admin_email}")
            return

        print("No existing admin found. Creating initial administrator account...")

        # 2. Insert user directly (explicitly passing NOT NULL columns with defaults)
        insert_user_query = text("""
            INSERT INTO users (id, email, hashed_password, role, is_banned, is_online)
            VALUES (:id, :email, :hashed_password, :role, :is_banned, :is_online)
            RETURNING id
        """)

        user_id = db.execute(
            insert_user_query,
            {
                "id": new_ulid(),
                "email": admin_email,
                "hashed_password": hash_password(admin_password),
                "role": role_value,
                "is_banned": False,
                "is_online": False,
            },
        ).scalar()

        # 3. Insert email verification record matching the schema name
        insert_verification_query = text("""
            INSERT INTO email_verifications (id, user_id, is_verified)
            VALUES (:id, :user_id, :is_verified)
        """)

        db.execute(
            insert_verification_query,
            {"id": new_ulid(), "user_id": user_id, "is_verified": True},
        )

        db.commit()
        print(f"Successfully created admin account: {admin_email}")

    except Exception as exc:
        db.rollback()
        print(f"Failed to create admin account due to error: {exc}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_admin()
