"""Add tag_id to calendar_events

Revision ID: 004
Revises: 003
Create Date: 2026-02-22 20:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add tag_id column to calendar_events table
    op.add_column(
        'calendar_events',
        sa.Column('tag_id', sa.String(), nullable=True)
    )
    # Add foreign key constraint
    op.create_foreign_key(
        'fk_calendar_events_tag_id_tags',
        'calendar_events', 'tags',
        ['tag_id'], ['id']
    )


def downgrade() -> None:
    op.drop_constraint(
        'fk_calendar_events_tag_id_tags',
        'calendar_events',
        type_='foreignkey'
    )
    op.drop_column('calendar_events', 'tag_id')
