"""add is_available to menu items

Revision ID: 008
Revises: 007
Create Date: 2025-01-04 18:40:52.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None

def upgrade():
    # Add is_available column with default value True
    op.add_column('menu_items', sa.Column('is_available', sa.Boolean(), nullable=False, server_default='1'))

def downgrade():
    # Remove is_available column
    op.drop_column('menu_items', 'is_available')
