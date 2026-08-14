"""
Docker Bootstrap Script

Purpose:
    Wait for DB connection, build database tables if needed,
    seed initial admin account, staff & customer user accounts,
    welding services, and welding inventory items.
"""

from __future__ import annotations

import sys
import time

from sqlalchemy import create_engine, text

from app.scripts.create_initial_admin import seed_admin
from app.scripts.seed_services_and_inventory import seed_services_and_inventory
from app.scripts.seed_users import seed_users_and_staff
from app.core.config import settings
from app.db import Base
import app.models  # noqa: F401


def wait_for_db(engine, max_retries: int = 30, delay: float = 1.0) -> None:
    print("Waiting for database connection...")
    for i in range(max_retries):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("Database connection established!")
            return
        except Exception as err:
            if i == max_retries - 1:
                print(f"Could not connect to DB after {max_retries} attempts: {err}")
                raise err
            time.sleep(delay)


def run_docker_bootstrap() -> None:
    db_url = settings.DATABASE_URL
    if not db_url:
        print("Error: DATABASE_URL not configured in settings.")
        sys.exit(1)

    engine = create_engine(db_url)
    wait_for_db(engine)

    print("Building database tables if not present...")
    Base.metadata.create_all(bind=engine)
    print("Database tables ready.")

    print("Seeding initial admin account...")
    try:
        seed_admin()
    except Exception as exc:
        print(f"Admin seeding step output: {exc}")

    print("Seeding initial staff and customer user accounts...")
    seed_users_and_staff()

    print("Seeding welding services and inventory items...")
    seed_services_and_inventory()

    print("Docker bootstrap completed successfully!")


if __name__ == "__main__":
    run_docker_bootstrap()
