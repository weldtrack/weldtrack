"""separate estimated and actual labor costs

Revision ID: 7e9c4f2a1b30
Revises: cd13fcbb3944
Create Date: 2026-08-29
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "7e9c4f2a1b30"
down_revision: Union[str, Sequence[str], None] = "cd13fcbb3944"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "bookings", sa.Column("estimated_labor_hours", sa.Float(), nullable=True)
    )
    op.add_column(
        "bookings", sa.Column("actual_labor_cost", sa.Float(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("bookings", "actual_labor_cost")
    op.drop_column("bookings", "estimated_labor_hours")
