"""update restaurant feedback table

Revision ID: e82bb45ddca9
Revises: d92aa45ddca8
Create Date: 2024-01-10

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic
revision = 'e82bb45ddca9'
down_revision = 'd92aa45ddca8'
branch_labels = None
depends_on = None

def upgrade():
    conn = op.get_bind()
    inspector = inspect(conn)
    
    # Check if the new table already exists
    if 'restaurant_feedback_new' not in inspector.get_table_names():
        # Create new table with updated schema
        op.create_table(
            'restaurant_feedback_new',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('feedback_text', sa.String(1000), nullable=False),
            sa.Column('service_rating', sa.Integer(), nullable=False),
            sa.Column('ambiance_rating', sa.Integer(), nullable=False),
            sa.Column('cleanliness_rating', sa.Integer(), nullable=False),
            sa.Column('value_rating', sa.Integer(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id'),
            sa.CheckConstraint('service_rating >= 1 AND service_rating <= 5', name='check_service_rating_range'),
            sa.CheckConstraint('ambiance_rating >= 1 AND ambiance_rating <= 5', name='check_ambiance_rating_range'),
            sa.CheckConstraint('cleanliness_rating >= 1 AND cleanliness_rating <= 5', name='check_cleanliness_rating_range'),
            sa.CheckConstraint('value_rating >= 1 AND value_rating <= 5', name='check_value_rating_range')
        )

        # Create index if it doesn't exist
        if not any(idx['name'] == 'ix_restaurant_feedback_new_user_id' for idx in inspector.get_indexes('restaurant_feedback_new')):
            op.create_index('ix_restaurant_feedback_new_user_id', 'restaurant_feedback_new', ['user_id'])

    # Copy data from old table to new table if old table exists
    if 'restaurant_feedback' in inspector.get_table_names():
        # Check if category column exists
        has_category = 'category' in [col['name'] for col in inspector.get_columns('restaurant_feedback')]
        
        if has_category:
            op.execute("""
                INSERT INTO restaurant_feedback_new (
                    id, user_id, feedback_text, service_rating, ambiance_rating, 
                    cleanliness_rating, value_rating, created_at, updated_at
                )
                SELECT 
                    id, user_id, feedback_text, 
                    CASE 
                        WHEN category = 'service' THEN 3
                        ELSE 3
                    END as service_rating,
                    CASE 
                        WHEN category = 'ambiance' THEN 3
                        ELSE 3
                    END as ambiance_rating,
                    CASE 
                        WHEN category = 'cleanliness' THEN 3
                        ELSE 3
                    END as cleanliness_rating,
                    3 as value_rating,
                    created_at, updated_at
                FROM restaurant_feedback
                WHERE id NOT IN (SELECT id FROM restaurant_feedback_new);
            """)
        else:
            op.execute("""
                INSERT INTO restaurant_feedback_new (
                    id, user_id, feedback_text, service_rating, ambiance_rating, 
                    cleanliness_rating, value_rating, created_at, updated_at
                )
                SELECT 
                    id, user_id, feedback_text, 
                    3 as service_rating,
                    3 as ambiance_rating,
                    3 as cleanliness_rating,
                    3 as value_rating,
                    created_at, updated_at
                FROM restaurant_feedback
                WHERE id NOT IN (SELECT id FROM restaurant_feedback_new);
            """)

        # Drop the old table
        op.drop_table('restaurant_feedback')

    # Rename the new table to the original name if it hasn't been done
    if 'restaurant_feedback_new' in inspector.get_table_names():
        op.rename_table('restaurant_feedback_new', 'restaurant_feedback')

def downgrade():
    # Create the original table
    op.create_table(
        'restaurant_feedback_old',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('feedback_text', sa.String(1000), nullable=False),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Copy data back with simplified categories
    op.execute("""
        INSERT INTO restaurant_feedback_old (
            id, user_id, feedback_text, category, created_at, updated_at
        )
        SELECT 
            id, user_id, feedback_text,
            CASE 
                WHEN service_rating >= 3 THEN 'service'
                WHEN ambiance_rating >= 3 THEN 'ambiance'
                WHEN cleanliness_rating >= 3 THEN 'cleanliness'
                ELSE 'general'
            END as category,
            created_at, updated_at
        FROM restaurant_feedback;
    """)

    # Drop the new version
    op.drop_table('restaurant_feedback')

    # Rename back to original name
    op.rename_table('restaurant_feedback_old', 'restaurant_feedback') 