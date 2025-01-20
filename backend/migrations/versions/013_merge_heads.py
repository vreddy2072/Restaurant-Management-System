"""merge heads

Revision ID: 013
Revises: 012, a3b11733ff0f
Create Date: 2024-01-10

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = '013'
down_revision = ('012', 'a3b11733ff0f')
branch_labels = None
depends_on = None

def upgrade():
    pass

def downgrade():
    pass 