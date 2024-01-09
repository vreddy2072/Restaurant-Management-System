"""Add is_guest column to users table

Revision ID: 004
Revises: 003
Create Date: 2025-01-04 10:23:24.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'  # Previous migration was 003
branch_labels = None
depends_on = None

def upgrade():
    # Add is_guest column with default value False
    op.add_column('users', 
        sa.Column('is_guest', sa.Boolean(), nullable=False, server_default='false')
    )

def downgrade():
    # Remove is_guest column
    op.drop_column('users', 'is_guest')
