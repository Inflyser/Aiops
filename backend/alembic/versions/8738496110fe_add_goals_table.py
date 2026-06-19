"""add goals table

Revision ID: 8738496110fe
Revises: 016
Create Date: 2026-06-19 10:58:57.410986

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8738496110fe'
down_revision: Union[str, None] = '016'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('goals',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('goal_type', sa.String(length=50), nullable=True),
        sa.Column('target_value', sa.Float(), nullable=True),
        sa.Column('target_unit', sa.String(length=50), nullable=True),
        sa.Column('current_value', sa.Float(), nullable=True),
        sa.Column('deadline', sa.DateTime(timezone=True), nullable=True),
        sa.Column('icon', sa.String(length=100), nullable=True),
        sa.Column('is_featured', sa.Boolean(), nullable=True),
        sa.Column('featured_position', sa.Integer(), nullable=True),
        sa.Column('order', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_goals_id'), 'goals', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_goals_id'), table_name='goals')
    op.drop_table('goals')




