"""add user_id to kanban columns

Revision ID: 015

Revises: 014

Create Date: 2024-03-29 21:28:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '015'
down_revision = '014'
branch_labels = None
depends_on = '014'


def upgrade() -> None:
    # Добавляем колонку user_id для Inbox категорий
    op.add_column('kanban_columns', sa.Column('user_id', sa.String(), nullable=True))
    
    # Создаем внешний ключ
    op.create_foreign_key(
        'fk_kanban_columns_user_id',
        'kanban_columns', 'users',
        ['user_id'], ['id']
    )


def downgrade() -> None:
    # Удаляем внешний ключ
    op.drop_constraint('fk_kanban_columns_user_id', 'kanban_columns', type_='foreignkey')
    
    # Удаляем колонку user_id
    op.drop_column('kanban_columns', 'user_id')
