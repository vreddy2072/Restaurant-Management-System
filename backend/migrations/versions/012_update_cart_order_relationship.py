"""update cart order relationship

Revision ID: 012
Revises: 011
Create Date: 2024-01-10

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic
revision = '012'
down_revision = '011'
branch_labels = None
depends_on = None

def upgrade():
    # Clean up any temporary tables that might exist from failed migrations
    conn = op.get_bind()
    conn.execute("DROP TABLE IF EXISTS _alembic_tmp_orders")
    conn.execute("DROP TABLE IF EXISTS _alembic_tmp_shopping_carts")
    
    inspector = inspect(conn)
    
    # Check if order_number column exists in shopping_carts
    shopping_cart_columns = [col['name'] for col in inspector.get_columns('shopping_carts')]
    if 'order_number' not in shopping_cart_columns:
        with op.batch_alter_table('shopping_carts') as batch_op:
            batch_op.add_column(sa.Column('order_number', sa.String(), nullable=True))

    # Drop cart_id index if it exists
    order_indexes = [idx['name'] for idx in inspector.get_indexes('orders')]
    if 'ix_orders_cart_id' in order_indexes:
        op.drop_index('ix_orders_cart_id', table_name='orders')

    # Check if cart_id exists in orders and drop it
    order_columns = [col['name'] for col in inspector.get_columns('orders')]
    if 'cart_id' in order_columns:
        with op.batch_alter_table('orders') as batch_op:
            batch_op.drop_column('cart_id')

def downgrade():
    # Add cart_id back to orders
    with op.batch_alter_table('orders') as batch_op:
        batch_op.add_column(sa.Column('cart_id', sa.Integer(), nullable=True))
    
    # Create index for cart_id
    op.create_index('ix_orders_cart_id', 'orders', ['cart_id'])

    # Remove order_number from shopping_carts
    with op.batch_alter_table('shopping_carts') as batch_op:
        batch_op.drop_column('order_number') 