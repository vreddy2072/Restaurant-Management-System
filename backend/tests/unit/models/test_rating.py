import pytest
from sqlalchemy.exc import IntegrityError
from backend.models.orm.rating import MenuItemRating, RestaurantFeedback

def test_create_menu_item_rating(db_session, test_user, sample_menu_item):
    rating = MenuItemRating(
        user_id=test_user.id,
        menu_item_id=sample_menu_item.id,
        rating=5,
        comment="Excellent dish!"
    )
    db_session.add(rating)
    db_session.commit()

    assert rating.id is not None
    assert rating.rating == 5
    assert rating.comment == "Excellent dish!"
    assert rating.created_at is not None
    assert rating.updated_at is not None

def test_invalid_rating_value(db_session, test_user, sample_menu_item):
    with pytest.raises(ValueError, match="Rating must be between 1 and 5"):
        rating = MenuItemRating(
            user_id=test_user.id,
            menu_item_id=sample_menu_item.id,
            rating=6
        )
        db_session.add(rating)
        db_session.commit()

def test_unique_user_menu_item_rating(db_session, test_user, sample_menu_item):
    # Create first rating
    rating1 = MenuItemRating(
        user_id=test_user.id,
        menu_item_id=sample_menu_item.id,
        rating=4
    )
    db_session.add(rating1)
    db_session.commit()

    # Try to create second rating for same user and menu item
    rating2 = MenuItemRating(
        user_id=test_user.id,
        menu_item_id=sample_menu_item.id,
        rating=5
    )
    db_session.add(rating2)
    with pytest.raises(IntegrityError):
        db_session.commit()

def test_create_restaurant_feedback(db_session, test_user):
    feedback = RestaurantFeedback(
        user_id=test_user.id,
        feedback_text="Great atmosphere and service",
        category="service"
    )
    db_session.add(feedback)
    db_session.commit()

    assert feedback.id is not None
    assert feedback.feedback_text == "Great atmosphere and service"
    assert feedback.category == "service"
    assert feedback.created_at is not None
    assert feedback.updated_at is not None

def test_invalid_feedback_category(db_session, test_user):
    with pytest.raises(ValueError, match="Invalid category"):
        feedback = RestaurantFeedback(
            user_id=test_user.id,
            feedback_text="Great place",
            category="invalid_category"
        )
        db_session.add(feedback)
        db_session.commit()

def test_empty_feedback_text(db_session, test_user):
    with pytest.raises(ValueError, match="Feedback text cannot be empty"):
        feedback = RestaurantFeedback(
            user_id=test_user.id,
            feedback_text="   ",
            category="service"
        )
        db_session.add(feedback)
        db_session.commit()

def test_rating_relationships(db_session, sample_menu_item_rating, test_user, sample_menu_item):
    # Test relationship with user
    assert sample_menu_item_rating.user.id == test_user.id
    
    # Test relationship with menu item
    assert sample_menu_item_rating.menu_item.id == sample_menu_item.id

def test_feedback_user_relationship(db_session, sample_restaurant_feedback, test_user):
    assert sample_restaurant_feedback.user.id == test_user.id

def test_cascade_delete_ratings(db_session, sample_menu_item, sample_menu_item_rating):
    # Delete menu item and verify rating is also deleted
    db_session.delete(sample_menu_item)
    db_session.commit()

    # Check if rating was deleted
    rating = db_session.query(MenuItemRating).filter_by(id=sample_menu_item_rating.id).first()
    assert rating is None
