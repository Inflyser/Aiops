"""add event tasks table

Revision ID: 010_add_event_tasks_table
Revises: 009_add_recurrence
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '010_add_event_tasks_table'
down_revision = '009_add_recurrence'
branch_labels = None
depends_on = None


def upgrade():
    # Create event_tasks table
    op.create_table(
        'event_tasks',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('event_id', sa.String(), nullable=False),
        sa.Column('task_id', sa.String(), nullable=False),
        sa.Column('order', sa.Integer(), server_default='0', nullable=False),
        sa.ForeignKeyConstraint(['event_id'], ['calendar_events.id'], ),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    # Create indexes for faster queries
    op.create_index(op.f('ix_event_tasks_event_id'), 'event_tasks', ['event_id'], unique=False)
    op.create_index(op.f('ix_event_tasks_task_id'), 'event_tasks', ['task_id'], unique=False)


def downgrade():
    # Drop indexes
    op.drop_index(op.f('ix_event_tasks_task_id'), table_name='event_tasks')
    op.drop_index(op.f('ix_event_tasks_event_id'), table_name='event_tasks')
    
    # Drop table
    op.drop_table('event_tasks')
