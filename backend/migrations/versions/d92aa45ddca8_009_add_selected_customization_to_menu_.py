"""009_add_selected_customization_to_menu_items

Revision ID: d92aa45ddca8
Revises: 008
Create Date: 2024-02-14

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = 'd92aa45ddca8'
down_revision = '008'
branch_labels = None
depends_on = None

def upgrade():
    # Add selected_customization column to menu_items table
    with op.batch_alter_table('menu_items') as batch_op:
        batch_op.add_column(sa.Column('selected_customization', sqlite.JSON, nullable=True))

def downgrade():
    # Remove selected_customization column from menu_items table
    with op.batch_alter_table('menu_items') as batch_op:
        batch_op.drop_column('selected_customization') 