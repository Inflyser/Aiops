"""add is_static to kanban columns

Revision ID: 011_add_is_static_to_kanban_columns
Revises: 010_add_event_tasks_table
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '011'
down_revision = '010'
branch_labels = None
depends_on = None


def upgrade():
    # Add is_static column to kanban_columns table
    op.add_column('kanban_columns', sa.Column('is_static', sa.Boolean(), server_default='0', nullable=False))
    
    # Update existing columns to set is_static=False
    op.execute("UPDATE kanban_columns SET is_static = FALSE WHERE is_static IS NULL")


def downgrade():
    # Remove is_static column from kanban_columns table
    op.drop_column('kanban_columns', 'is_static')
