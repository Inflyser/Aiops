"""add is_inbox_category to kanban columns

Revision ID: 014

Revises: 013

Create Date: 2024-03-29 16:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '014'
down_revision = '013'
branch_labels = None
depends_on = '013'


def upgrade() -> None:
    # Добавляем колонку is_inbox_category
    op.add_column('kanban_columns', sa.Column('is_inbox_category', sa.Boolean(), nullable=False, server_default='false'))
    
    # Делаем board_id nullable для Inbox категорий
    op.alter_column('kanban_columns', 'board_id', nullable=True)


def downgrade() -> None:
    # Удаляем колонку is_inbox_category
    op.drop_column('kanban_columns', 'is_inbox_category')
    
    # Делаем board_id not nullable обратно
    op.alter_column('kanban_columns', 'board_id', nullable=False)
