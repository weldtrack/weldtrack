import os
from collections.abc import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def ensure_runtime_schema() -> None:
    """Apply additive schema repairs for deployments without migrations."""
    inspector = inspect(engine)
    repairs = {
        "staff_tasks": [
            ("booking_id", 'INTEGER'),
        ],
        "task_material_usages": [
            ("booking_id", 'INTEGER'),
        ],
        "staff_contribution_snapshots": [
            ("booking_id", 'INTEGER'),
        ],
    }

    with engine.begin() as connection:
        for table_name, columns in repairs.items():
            if not inspector.has_table(table_name):
                continue

            existing_columns = {
                column["name"]
                for column in inspector.get_columns(table_name)
            }
            for column_name, column_type in columns:
                if column_name in existing_columns:
                    continue
                connection.execute(
                    text(
                        f'ALTER TABLE "{table_name}" '
                        f'ADD COLUMN "{column_name}" {column_type}'
                    )
                )


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
