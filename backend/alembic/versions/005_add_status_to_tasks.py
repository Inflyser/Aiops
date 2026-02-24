"""Add status to tasks

Revision ID: 005
Revises: 004
Create Date: 2026-02-24 20:54:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Добавляем колонку status со значением по умолчанию 'todo'
    op.add_column('tasks', sa.Column('status', sa.String(50), nullable=True))
    
    # Устанавливаем значение по умолчанию для существующих записей
    # Задачи с completed=True получают статус 'done', остальные - 'todo'
    op.execute("UPDATE tasks SET status = CASE WHEN completed = true THEN 'done' ELSE 'todo' END WHERE status IS NULL")
    
    # Теперь делаем колонку NOT NULL
    op.alter_column('tasks', 'status', nullable=False)


def downgrade() -> None:
    op.drop_column('tasks', 'status')
