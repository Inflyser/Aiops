"""add icon to tags

Revision ID: 008_add_icon_to_tags
Revises: 007_make_priority_nullable
Create Date: 2026-03-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '008_add_icon_to_tags'
down_revision = '007_make_priority_nullable'
branch_labels = None
depends_on = None

def upgrade() -> None:
    conn = op.get_bind()
    
    # Проверяем, существует ли колонка icon
    result = conn.execute(sa.text("SELECT column_name FROM information_schema.columns WHERE table_name = 'tags' AND column_name = 'icon'"))
    if not result.fetchone():
        op.add_column('tags', sa.Column('icon', sa.String(100), nullable=True))

def downgrade() -> None:
    op.drop_column('tags', 'icon')
