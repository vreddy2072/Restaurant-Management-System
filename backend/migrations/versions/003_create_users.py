"""create users table

Revision ID: 003
Revises: 002
Create Date: 2025-01-02 21:18:21

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(50), nullable=False, unique=True),
        sa.Column('email', sa.String(100), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('first_name', sa.String(50), nullable=False),
        sa.Column('last_name', sa.String(50), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('phone_number', sa.String(20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_username', 'users', ['username'], unique=True)
    
    # Create triggers for timestamp management
    op.execute('''
        CREATE TRIGGER users_insert_trigger
        AFTER INSERT ON users
        BEGIN
            UPDATE users 
            SET created_at = DATETIME('now'),
                updated_at = DATETIME('now')
            WHERE id = NEW.id;
        END;
    ''')
    
    op.execute('''
        CREATE TRIGGER users_update_trigger
        AFTER UPDATE ON users
        BEGIN
            UPDATE users 
            SET updated_at = DATETIME('now')
            WHERE id = NEW.id;
        END;
    ''')


def downgrade() -> None:
    # Drop triggers first
    op.execute('DROP TRIGGER IF EXISTS users_update_trigger')
    op.execute('DROP TRIGGER IF EXISTS users_insert_trigger')
    
    # Drop indexes
    op.drop_index('ix_users_username')
    op.drop_index('ix_users_email')
    
    # Drop table
    op.drop_table('users')
