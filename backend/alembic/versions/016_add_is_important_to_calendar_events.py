"""Add is_important to calendar_events

Revision ID: 016
Revises: 015
Create Date: 2026-05-18

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '016'
down_revision = '015'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('calendar_events', sa.Column('is_important', sa.Boolean(), default=False, server_default='false'))


def downgrade() -> None:
    op.drop_column('calendar_events', 'is_important')