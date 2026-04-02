"""add kanban_boards table

Revision ID: 012_add_kanban_boards_table
Revises: 011_add_is_static_to_kanban_columns
Create Date: 2026-03-22 11:23:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column, text
from uuid import uuid4


# revision identifiers, used by Alembic.
revision = '012'
down_revision = '011'
branch_labels = None
depends_on = None


def upgrade():
    # Create kanban_boards table
    op.create_table(
        'kanban_boards',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('board_order', sa.Integer(), nullable=True),
        sa.Column('is_default', sa.Boolean(), nullable=True),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_kanban_boards_id'), 'kanban_boards', ['id'], unique=False)
    
    # Add board_id column to kanban_columns
    op.add_column('kanban_columns', sa.Column('board_id', sa.String(), nullable=True))
    
    # Create foreign key constraint
    op.create_foreign_key(
        'fk_kanban_columns_board_id_kanban_boards',
        'kanban_columns', 'kanban_boards',
        ['board_id'], ['id']
    )
    
    # Get connection and metadata
    conn = op.get_bind()
    metadata = sa.MetaData()
    
    # Define tables
    users_table = table('users', column('id', sa.String))
    kanban_boards_table = table('kanban_boards',
        column('id', sa.String),
        column('title', sa.String),
        column('board_order', sa.Integer),
        column('is_default', sa.Boolean),
        column('user_id', sa.String)
    )
    kanban_columns_table = table('kanban_columns',
        column('id', sa.String),
        column('board_id', sa.String),
        column('user_id', sa.String)
    )
    
    # Get all users
    result = conn.execute(sa.select(users_table.c.id))
    users = result.fetchall()
    
    for user in users:
        user_id = user[0]
        board_id = str(uuid4())
        
        # Insert default board using text() with parameterized query
        conn.execute(
            text("""
                INSERT INTO kanban_boards (id, title, "board_order", is_default, user_id)
                VALUES (:board_id, 'Default', 0, true, :user_id)
            """),
            {"board_id": board_id, "user_id": user_id}
        )
        
        # Update existing columns to point to new board
        conn.execute(
            text("""
                UPDATE kanban_columns
                SET board_id = :board_id
                WHERE user_id = :user_id
            """),
            {"board_id": board_id, "user_id": user_id}
        )
    
    # Make board_id NOT NULL after all columns are updated
    op.alter_column('kanban_columns', 'board_id', nullable=False)
    
    # Drop user_id from kanban_columns (no longer needed)
    op.drop_constraint('kanban_columns_user_id_fkey', 'kanban_columns', type_='foreignkey')
    op.drop_column('kanban_columns', 'user_id')


def downgrade():
    # Add user_id back to kanban_columns
    op.add_column('kanban_columns', sa.Column('user_id', sa.String(), nullable=True))
    
    # Restore user_id from board
    conn = op.get_bind()
    metadata = sa.MetaData()
    
    kanban_columns_table = table('kanban_columns',
        column('id', sa.String),
        column('board_id', sa.String),
        column('user_id', sa.String)
    )
    kanban_boards_table = table('kanban_boards',
        column('id', sa.String),
        column('user_id', sa.String)
    )
    
    conn.execute(
        text("""
            UPDATE kanban_columns kc
            SET user_id = (SELECT user_id FROM kanban_boards WHERE id = kc.board_id)
        """)
    )
    
    op.alter_column('kanban_columns', 'user_id', nullable=False)
    
    # Create foreign key constraint
    op.create_foreign_key(
        'kanban_columns_user_id_fkey',
        'kanban_columns', 'users',
        ['user_id'], ['id']
    )
    
    # Drop board_id and constraint
    op.drop_constraint('fk_kanban_columns_board_id_kanban_boards', 'kanban_columns', type_='foreignkey')
    op.drop_column('kanban_columns', 'board_id')
    
    # Drop kanban_boards table
    op.drop_index(op.f('ix_kanban_boards_id'), table_name='kanban_boards')
    op.drop_table('kanban_boards')
