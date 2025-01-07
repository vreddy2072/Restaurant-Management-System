"""add ratings and feedback

Revision ID: 007
Revises: 006
Create Date: 2025-01-04 11:34:26.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None

def upgrade():
    # Create menu item ratings table
    op.create_table(
        'menu_item_ratings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('menu_item_id', sa.Integer(), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('comment', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['menu_item_id'], ['menu_items.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range'),
        sa.UniqueConstraint('user_id', 'menu_item_id', name='uq_user_menu_item_rating')
    )

    # Create restaurant feedback table
    op.create_table(
        'restaurant_feedback',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('feedback_text', sa.String(1000), nullable=False),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index(op.f('ix_menu_item_ratings_user_id'), 'menu_item_ratings', ['user_id'], unique=False)
    op.create_index(op.f('ix_menu_item_ratings_menu_item_id'), 'menu_item_ratings', ['menu_item_id'], unique=False)
    op.create_index(op.f('ix_restaurant_feedback_user_id'), 'restaurant_feedback', ['user_id'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_restaurant_feedback_user_id'), table_name='restaurant_feedback')
    op.drop_index(op.f('ix_menu_item_ratings_menu_item_id'), table_name='menu_item_ratings')
    op.drop_index(op.f('ix_menu_item_ratings_user_id'), table_name='menu_item_ratings')
    op.drop_table('restaurant_feedback')
    op.drop_table('menu_item_ratings')
