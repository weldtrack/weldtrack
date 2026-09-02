"""add service pricing type and fixed price

Revision ID: b81f5c3e7a20
Revises: a41f8c2d9e70
Create Date: 2026-09-02
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b81f5c3e7a20"
down_revision: Union[str, Sequence[str], None] = "a41f8c2d9e70"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "services",
        sa.Column(
            "pricing_type",
            sa.String(length=32),
            nullable=False,
            server_default="hourly",
        ),
    )
    op.add_column(
        "services",
        sa.Column(
            "price_fixed",
            sa.Float(),
            nullable=False,
            server_default="0.0",
        ),
    )


def downgrade() -> None:
    op.drop_column("services", "price_fixed")
    op.drop_column("services", "pricing_type")
