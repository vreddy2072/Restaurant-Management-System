"""010_update_restaurant_feedback_table

Revision ID: e82bb45ddca9
Revises: d92aa45ddca8
Create Date: 2024-01-05

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision = 'e82bb45ddca9'
down_revision = 'd92aa45ddca8'
branch_labels = None
depends_on = None


def upgrade():
    # Create new table with updated schema
    op.create_table(
        'restaurant_feedback_new',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('feedback_text', sa.String(1000), nullable=False),
        sa.Column('service_rating', sa.Integer(), nullable=False),
        sa.Column('ambiance_rating', sa.Integer(), nullable=False),
        sa.Column('cleanliness_rating', sa.Integer(), nullable=False),
        sa.Column('value_rating', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.CheckConstraint('service_rating >= 1 AND service_rating <= 5', name='check_service_rating_range'),
        sa.CheckConstraint('ambiance_rating >= 1 AND ambiance_rating <= 5', name='check_ambiance_rating_range'),
        sa.CheckConstraint('cleanliness_rating >= 1 AND cleanliness_rating <= 5', name='check_cleanliness_rating_range'),
        sa.CheckConstraint('value_rating >= 1 AND value_rating <= 5', name='check_value_rating_range'),
    )

    # Copy data from old table to new table with default values for new columns
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    
    if 'restaurant_feedback' in inspector.get_table_names():
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
            FROM restaurant_feedback;
        """)

        # Drop the old table
        op.drop_table('restaurant_feedback')

    # Rename the new table to the original name
    op.rename_table('restaurant_feedback_new', 'restaurant_feedback')


def downgrade():
    # Create the original table
    op.create_table(
        'restaurant_feedback_old',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('feedback_text', sa.String(1000), nullable=False),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    # Copy data back to the original format
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    
    if 'restaurant_feedback' in inspector.get_table_names():
        op.execute("""
            INSERT INTO restaurant_feedback_old (
                id, user_id, feedback_text, category, created_at, updated_at
            )
            SELECT 
                id, user_id, feedback_text,
                CASE 
                    WHEN service_rating >= 4 THEN 'service'
                    WHEN ambiance_rating >= 4 THEN 'ambiance'
                    WHEN cleanliness_rating >= 4 THEN 'cleanliness'
                    ELSE 'other'
                END as category,
                created_at, updated_at
            FROM restaurant_feedback;
        """)

        # Drop the new table
        op.drop_table('restaurant_feedback')

    # Rename back to original name
    op.rename_table('restaurant_feedback_old', 'restaurant_feedback') 