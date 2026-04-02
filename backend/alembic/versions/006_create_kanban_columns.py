"""Create kanban_columns table

Revision ID: 006
Revises: 005
Create Date: 2026-02-24 23:40:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    
    # Создаем таблицу kanban_columns если не существует
    result = conn.execute(sa.text("SELECT table_name FROM information_schema.tables WHERE table_name = 'kanban_columns'"))
    if result.fetchone() is None:
        op.create_table(
            'kanban_columns',
            sa.Column('id', sa.String(), primary_key=True),
            sa.Column('title', sa.String(255), nullable=False),
            sa.Column('order', sa.Integer(), default=0),
            sa.Column('color', sa.String(7), default='#555555'),
            sa.Column('user_id', sa.String(), sa.ForeignKey('users.id'), nullable=False),
        )
    
    # Добавляем column_id в tasks если не существует
    result = conn.execute(sa.text("SELECT column_name FROM information_schema.columns WHERE table_name = 'tasks' AND column_name = 'column_id'"))
    if result.fetchone() is None:
        op.add_column('tasks', sa.Column('column_id', sa.String(), sa.ForeignKey('kanban_columns.id'), nullable=True))


def downgrade() -> None:
    op.drop_column('tasks', 'column_id')
    op.drop_table('kanban_columns')
