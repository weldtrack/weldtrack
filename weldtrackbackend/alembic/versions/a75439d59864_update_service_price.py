"""update service price

Revision ID: a75439d59864
Revises: 
Create Date: 2026-06-28 14:23:49.557551

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a75439d59864'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('booking_history',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('booking_id', sa.Integer(), nullable=False),
    sa.Column('action', sa.Enum('created', 'confirmed', 'scheduled', 'completed', 'cancelled', 'updated', name='bookinghistoryaction'), nullable=False),
    sa.Column('note', sa.Text(), nullable=True),
    sa.Column('changed_by', sa.String(length=100), nullable=True),
    sa.Column('status_from', sa.String(length=50), nullable=True),
    sa.Column('status_to', sa.String(length=50), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['booking_id'], ['bookings.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_booking_history_booking_id'), 'booking_history', ['booking_id'], unique=False)
    op.create_index(op.f('ix_booking_history_id'), 'booking_history', ['id'], unique=False)
    op.create_table('project_history',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('booking_id', sa.Integer(), nullable=True),
    sa.Column('task_id', sa.String(length=100), nullable=True),
    sa.Column('action', sa.Enum('created', 'started', 'updated', 'note_added', 'completed', 'cancelled', name='projecthistoryaction'), nullable=False),
    sa.Column('note', sa.Text(), nullable=True),
    sa.Column('changed_by', sa.String(length=100), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['booking_id'], ['bookings.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_project_history_booking_id'), 'project_history', ['booking_id'], unique=False)
    op.create_index(op.f('ix_project_history_id'), 'project_history', ['id'], unique=False)
    op.create_index(op.f('ix_project_history_task_id'), 'project_history', ['task_id'], unique=False)
    op.execute("ALTER TABLE attendance_records DROP COLUMN IF EXISTS total_hours_worked")
    op.alter_column('feedback_comments', 'date',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
    op.execute("ALTER TABLE feedback_comments DROP CONSTRAINT IF EXISTS fk_feedback_comments_feedback")
    op.create_foreign_key(None, 'feedback_comments', 'feedbacks', ['feedback_id'], ['id'])
    op.execute("ALTER TABLE feedback_likes DROP CONSTRAINT IF EXISTS fk_feedback_likes_feedback")
    op.create_foreign_key(None, 'feedback_likes', 'feedbacks', ['feedback_id'], ['id'])
    op.add_column('task_material_usages', sa.Column('labor_hours', sa.Float(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('task_material_usages', 'labor_hours')
    op.drop_constraint(None, 'feedback_likes', type_='foreignkey')
    op.create_foreign_key(op.f('fk_feedback_likes_feedback'), 'feedback_likes', 'feedbacks', ['feedback_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint(None, 'feedback_comments', type_='foreignkey')
    op.create_foreign_key(op.f('fk_feedback_comments_feedback'), 'feedback_comments', 'feedbacks', ['feedback_id'], ['id'], ondelete='CASCADE')
    op.alter_column('feedback_comments', 'date',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
    op.add_column('attendance_records', sa.Column('total_hours_worked', sa.NUMERIC(precision=5, scale=2), autoincrement=False, nullable=True))
    op.drop_index(op.f('ix_project_history_task_id'), table_name='project_history')
    op.drop_index(op.f('ix_project_history_id'), table_name='project_history')
    op.drop_index(op.f('ix_project_history_booking_id'), table_name='project_history')
    op.drop_table('project_history')
    op.drop_index(op.f('ix_booking_history_id'), table_name='booking_history')
    op.drop_index(op.f('ix_booking_history_booking_id'), table_name='booking_history')
    op.drop_table('booking_history')
