"""make priority nullable

Revision ID: 007_make_priority_nullable
Revises: 006_create_kanban_columns
Create Date: 2026-02-26 13:15:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '007_make_priority_nullable'
down_revision = '006_create_kanban_columns'
branch_labels = None
depends_on = None

def upgrade() -> None:
    conn = op.get_bind()
    
    # Проверяем, является ли колонка уже nullable
    result = conn.execute(sa.text("SELECT is_nullable FROM information_schema.columns WHERE table_name = 'tasks' AND column_name = 'priority'"))
    row = result.fetchone()
    if row and row[0] == 'NO':
        # Устанавливаем всем задачам с 'medium' приоритетом значение NULL
        conn.execute(sa.text("UPDATE tasks SET priority = NULL WHERE priority = 'medium'"))
        
        # Колонка не nullable - делаем её nullable
        op.alter_column('tasks', 'priority',
                   existing_type=sa.String(20),
                   nullable=True)

def downgrade() -> None:
    # Revert to not nullable with default
    op.alter_column('tasks', 'priority',
               existing_type=sa.String(20),
               nullable=False,
               existing_server_default='medium')
