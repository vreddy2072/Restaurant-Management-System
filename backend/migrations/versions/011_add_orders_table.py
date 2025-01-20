"""Add orders table

Revision ID: 011
Revises: d92aa45ddca8
Create Date: 2024-01-10

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = '011'
down_revision = 'd92aa45ddca8'
branch_labels = None
depends_on = None

def upgrade():
    # Create orders table
    op.create_table(
        'orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_number', sa.String(50), nullable=False, unique=True),
        sa.Column('table_number', sa.Integer(), nullable=False),
        sa.Column('customer_name', sa.String(100), nullable=False),
        sa.Column('is_group_order', sa.Boolean(), nullable=False, default=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('cart_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, default='initialized'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        
        # Primary key
        sa.PrimaryKeyConstraint('id'),
        
        # Foreign keys
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['cart_id'], ['shopping_carts.id'], ondelete='SET NULL'),
        
        # Check constraints
        sa.CheckConstraint('table_number >= 1 AND table_number <= 10', name='check_table_number_range'),
        sa.CheckConstraint("status IN ('initialized', 'in_progress', 'confirmed', 'completed', 'cancelled')", name='check_valid_status')
    )
    
    # Create indexes
    op.create_index('ix_orders_order_number', 'orders', ['order_number'], unique=True)
    op.create_index('ix_orders_user_id', 'orders', ['user_id'])
    op.create_index('ix_orders_cart_id', 'orders', ['cart_id'])
    op.create_index('ix_orders_status', 'orders', ['status'])
    op.create_index('ix_orders_created_at', 'orders', ['created_at'])

def downgrade():
    # Drop indexes first
    op.drop_index('ix_orders_created_at')
    op.drop_index('ix_orders_status')
    op.drop_index('ix_orders_cart_id')
    op.drop_index('ix_orders_user_id')
    op.drop_index('ix_orders_order_number')
    
    # Drop the table
    op.drop_table('orders') 