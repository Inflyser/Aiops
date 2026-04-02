"""remove inbox column and is_default flag

Revision ID: 013_remove_inbox_column_and_is_default
Revises: 012_add_kanban_boards_table
Create Date: 2026-03-27 21:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column, text


# revision identifiers, used by Alembic.
revision = '013'
down_revision = '012'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    
    # First, set column_id to NULL for tasks that reference Inbox columns
    conn.execute(
        text("""
            UPDATE tasks
            SET column_id = NULL
            WHERE column_id IN (
                SELECT id FROM kanban_columns WHERE title = 'Inbox'
            )
        """)
    )
    
    # Then delete Inbox columns from all boards
    conn.execute(
        text("""
            DELETE FROM kanban_columns
            WHERE title = 'Inbox'
        """)
    )
    
    # Drop is_default column from kanban_boards
    op.drop_column('kanban_boards', 'is_default')


def downgrade():
    # Add is_default column back
    op.add_column('kanban_boards', sa.Column('is_default', sa.Boolean(), nullable=True))
    
    # Set first board as default for each user
    conn = op.get_bind()
    conn.execute(
        text("""
            UPDATE kanban_boards
            SET is_default = true
            WHERE id IN (
                SELECT MIN(id)
                FROM kanban_boards
                GROUP BY user_id
            )
        """)
    )
