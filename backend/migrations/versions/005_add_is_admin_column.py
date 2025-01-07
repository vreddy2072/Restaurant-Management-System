"""Add is_admin column to users table

Revision ID: 005
Revises: 004
Create Date: 2025-01-04 10:39:32.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None

def upgrade():
    # Add is_admin column with default value False
    op.add_column('users', 
        sa.Column('is_admin', sa.Boolean(), nullable=False, server_default='false')
    )
    
    # Update existing admin role users to have is_admin=True
    op.execute("""
        UPDATE users 
        SET is_admin = true 
        WHERE role = 'admin'
    """)

def downgrade():
    # Remove is_admin column
    op.drop_column('users', 'is_admin')
