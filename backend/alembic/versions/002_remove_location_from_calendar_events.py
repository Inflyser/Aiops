"""Remove location column from calendar_events

Revision ID: 002
Revises: 001
Create Date: 2026-02-21

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Remove location column from calendar_events table
    op.drop_column('calendar_events', 'location')


def downgrade() -> None:
    # Add back location column if needed
    op.add_column('calendar_events', sa.Column('location', sa.String(255), nullable=True))
