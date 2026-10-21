"""
User and Staff Seed Script

Purpose:
    Seeds initial staff and customer user accounts with pre-configured passwords.
"""

from __future__ import annotations

from sqlalchemy import text

from app.core.config import settings

from app.core.id import new_ulid
from app.core.security import hash_password
from app.db import SessionLocal
from app.models.user import UserRole


# Initial seed accounts with passwords specified directly in script
SEED_STAFF_USERS = [
    {
        "email": "staff1@weldtrack.com",
        "full_name": "Juan Dela Cruz",
        "password": "Staff123!@#",
        "role": UserRole.staff.value if hasattr(UserRole.staff, "value") else UserRole.staff,
        "mobile_phone": "+639170000001",
    },
    {
        "email": "staff2@weldtrack.com",
        "full_name": "Marco Santos",
        "password": "Staff123!@#",
        "role": UserRole.staff.value if hasattr(UserRole.staff, "value") else UserRole.staff,
        "mobile_phone": "+639170000002",
    },
    {
        "email": "ramon.reyes@weldtrack.com",
        "full_name": "Ramon Reyes",
        "password": "Staff123!@#",
        "role": UserRole.staff.value if hasattr(UserRole.staff, "value") else UserRole.staff,
        "mobile_phone": "+639170000005",
    },
    {
        "email": "carlo.mendoza@weldtrack.com",
        "full_name": "Carlo Mendoza",
        "password": "Staff123!@#",
        "role": UserRole.staff.value if hasattr(UserRole.staff, "value") else UserRole.staff,
        "mobile_phone": "+639170000006",
    },
]

SEED_CUSTOMER_USERS = [
    {
        "email": "user1@weldtrack.com",
        "full_name": "Maria Clara Gobole",
        "password": "User123!@#",
        "role": UserRole.customer.value if hasattr(UserRole.customer, "value") else UserRole.customer,
        "mobile_phone": "+639170000003",
    },
    {
        "email": "user2@weldtrack.com",
        "full_name": "Jose Rizalino",
        "password": "User123!@#",
        "role": UserRole.customer.value if hasattr(UserRole.customer, "value") else UserRole.customer,
        "mobile_phone": "+639170000004",
    },
]


def seed_users_and_staff() -> None:
    db = SessionLocal()
    try:
        db.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS full_name VARCHAR(255)"))
        db.commit()

        all_seeds = SEED_STAFF_USERS + SEED_CUSTOMER_USERS
        for account in all_seeds:
            email = account["email"]
            full_name = account.get("full_name")
            password = account["password"]
            role = account["role"]
            mobile_phone = account.get("mobile_phone")

            # Check if user already exists
            existing = db.execute(
                text("SELECT id, full_name FROM users WHERE email = :email LIMIT 1"),
                {"email": email},
            ).fetchone()

            if existing:
                if full_name and not existing.full_name:
                    db.execute(
                        text("UPDATE users SET full_name = :full_name WHERE id = :id"),
                        {"full_name": full_name, "id": existing.id},
                    )
                    print(f"Updated full_name for existing user: {email} -> {full_name}")
                else:
                    print(f"User already exists: {email} (role: {role})")
                continue

            print(f"Creating account: {email} ({full_name}, role: {role})...")
            user_id = new_ulid()
            insert_user_query = text("""
                INSERT INTO users (id, email, full_name, hashed_password, role, is_banned, is_online, mobile_phone)
                VALUES (:id, :email, :full_name, :hashed_password, :role, :is_banned, :is_online, :mobile_phone)
            """)
            db.execute(
                insert_user_query,
                {
                    "id": user_id,
                    "email": email,
                    "full_name": full_name,
                    "hashed_password": hash_password(password),
                    "role": role,
                    "is_banned": False,
                    "is_online": False,
                    "mobile_phone": mobile_phone,
                },
            )

            # Insert email verification
            insert_verification_query = text("""
                INSERT INTO email_verifications (id, user_id, is_verified)
                VALUES (:id, :user_id, :is_verified)
            """)
            db.execute(
                insert_verification_query,
                {"id": new_ulid(), "user_id": user_id, "is_verified": True},
            )
            print(f"Successfully created account: {email}")

        db.commit()
    except Exception as exc:
        db.rollback()
        print(f"Failed to seed users and staff due to error: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_users_and_staff()
