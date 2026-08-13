"""rename service price to price hour

Revision ID: df62f3e8f167
Revises: 5a26f6e4eb9f
Create Date: 2026-08-13 22:58:14.263935

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'df62f3e8f167'
down_revision: Union[str, Sequence[str], None] = '5a26f6e4eb9f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        'services',
        'price',
        new_column_name='price_hour',
        existing_type=sa.DOUBLE_PRECISION(precision=53),
        existing_nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        'services',
        'price_hour',
        new_column_name='price',
        existing_type=sa.DOUBLE_PRECISION(precision=53),
        existing_nullable=False,
    )
