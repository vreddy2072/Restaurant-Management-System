"""add allergens and customization

Revision ID: 002
Revises: 001
Create Date: 2024-02-14

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None

def upgrade():
    # Create allergens table
    op.create_table(
        'allergens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_allergens_name'), 'allergens', ['name'], unique=True)

    # Create menu_item_allergens junction table
    op.create_table(
        'menu_item_allergens',
        sa.Column('menu_item_id', sa.Integer(), nullable=False),
        sa.Column('allergen_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['allergen_id'], ['allergens.id'], ),
        sa.ForeignKeyConstraint(['menu_item_id'], ['menu_items.id'], ),
        sa.PrimaryKeyConstraint('menu_item_id', 'allergen_id')
    )

    # Add new columns to menu_items table
    with op.batch_alter_table('menu_items') as batch_op:
        batch_op.add_column(sa.Column('customization_options', sqlite.JSON, nullable=True))
        batch_op.add_column(sa.Column('average_rating', sa.Float(), nullable=False, server_default='0.0'))
        batch_op.add_column(sa.Column('rating_count', sa.Integer(), nullable=False, server_default='0'))

def downgrade():
    # Remove new columns from menu_items table
    with op.batch_alter_table('menu_items') as batch_op:
        batch_op.drop_column('rating_count')
        batch_op.drop_column('average_rating')
        batch_op.drop_column('customization_options')

    # Drop menu_item_allergens junction table
    op.drop_table('menu_item_allergens')

    # Drop allergens table
    op.drop_index(op.f('ix_allergens_name'), table_name='allergens')
    op.drop_table('allergens') 