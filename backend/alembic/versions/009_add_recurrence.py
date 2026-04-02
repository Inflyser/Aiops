"""add recurrence fields to calendar events

Revision ID: 009_add_recurrence
Revises: 008_add_icon_to_tags
Create Date: 2026-03-02 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '009'
down_revision = '008'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column('calendar_events', sa.Column('recurrence_type', sa.String(20), nullable=True))
    op.add_column('calendar_events', sa.Column('recurrence_days', sa.String(20), nullable=True))
    op.add_column('calendar_events', sa.Column('recurrence_end_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('calendar_events', sa.Column('recurrence_count', sa.Integer, nullable=True))

def downgrade() -> None:
    op.drop_column('calendar_events', 'recurrence_count')
    op.drop_column('calendar_events', 'recurrence_end_date')
    op.drop_column('calendar_events', 'recurrence_days')
    op.drop_column('calendar_events', 'recurrence_type')
