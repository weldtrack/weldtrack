"""archive inventory items instead of deleting them

Revision ID: a41f8c2d9e70
Revises: 7e9c4f2a1b30
Create Date: 2026-08-29
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a41f8c2d9e70"
down_revision: Union[str, Sequence[str], None] = "7e9c4f2a1b30"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "inventory_items",
        sa.Column("is_archived", sa.Boolean(), server_default=sa.false(), nullable=False),
    )
    op.add_column(
        "inventory_items",
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_inventory_items_is_archived", "inventory_items", ["is_archived"])


def downgrade() -> None:
    op.drop_index("ix_inventory_items_is_archived", table_name="inventory_items")
    op.drop_column("inventory_items", "archived_at")
    op.drop_column("inventory_items", "is_archived")
