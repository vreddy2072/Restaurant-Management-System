import pytest
from datetime import datetime
from sqlalchemy.orm import Session

from backend.services.rating_service import RatingService
from backend.models.schemas.rating import RestaurantFeedbackCreate
from backend.models.orm.rating import RestaurantFeedback
from backend.models.orm.user import User

@pytest.fixture
def test_user(db_session: Session) -> User:
    """Create a test user for testing."""
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash="hashedpass123",
        first_name="Test",
        last_name="User",
        role="customer"
    )
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def rating_service(db_session: Session) -> RatingService:
    """Create a RatingService instance for testing."""
    return RatingService(db_session)

def test_create_restaurant_feedback(db_session: Session, rating_service: RatingService, test_user: User):
    # Create a new restaurant feedback
    feedback_data = RestaurantFeedbackCreate(
        feedback_text="Great experience overall!",
        service_rating=5,
        ambiance_rating=4,
        cleanliness_rating=5,
        value_rating=4
    )
    feedback = rating_service.create_restaurant_feedback(feedback_data, test_user.id)
    
    # Verify the feedback was created correctly
    assert feedback.user_id == test_user.id
    assert feedback.feedback_text == feedback_data.feedback_text
    assert feedback.service_rating == feedback_data.service_rating
    assert feedback.ambiance_rating == feedback_data.ambiance_rating
    assert feedback.cleanliness_rating == feedback_data.cleanliness_rating
    assert feedback.value_rating == feedback_data.value_rating

def test_get_restaurant_feedback(db_session: Session, rating_service: RatingService, test_user: User):
    # Create multiple feedback entries
    feedback_data_list = [
        RestaurantFeedbackCreate(
            feedback_text="Great service!",
            service_rating=5,
            ambiance_rating=4,
            cleanliness_rating=5,
            value_rating=4
        ),
        RestaurantFeedbackCreate(
            feedback_text="Good food but slow service",
            service_rating=3,
            ambiance_rating=4,
            cleanliness_rating=4,
            value_rating=3
        )
    ]
    
    for feedback_data in feedback_data_list:
        rating_service.create_restaurant_feedback(feedback_data, test_user.id)
    
    # Get all feedback
    all_feedback = rating_service.get_restaurant_feedback()
    assert len(all_feedback) == 2

def test_get_user_feedback(db_session: Session, rating_service: RatingService, test_user: User):
    # Create feedback for the test user
    feedback_data = RestaurantFeedbackCreate(
        feedback_text="Excellent experience!",
        service_rating=5,
        ambiance_rating=5,
        cleanliness_rating=5,
        value_rating=5
    )
    rating_service.create_restaurant_feedback(feedback_data, test_user.id)
    
    # Get user's feedback
    user_feedback = rating_service.get_user_feedback(test_user.id)
    assert len(user_feedback) == 1
    assert user_feedback[0].user_id == test_user.id
    assert user_feedback[0].feedback_text == feedback_data.feedback_text

def test_get_restaurant_feedback_stats(db_session: Session, rating_service: RatingService, test_user: User):
    # Create multiple feedback entries
    feedback_data_list = [
        RestaurantFeedbackCreate(
            feedback_text="Great service!",
            service_rating=5,
            ambiance_rating=4,
            cleanliness_rating=5,
            value_rating=4
        ),
        RestaurantFeedbackCreate(
            feedback_text="Good food but slow service",
            service_rating=3,
            ambiance_rating=4,
            cleanliness_rating=4,
            value_rating=3
        )
    ]
    
    for feedback_data in feedback_data_list:
        rating_service.create_restaurant_feedback(feedback_data, test_user.id)
    
    # Get feedback stats
    stats = rating_service.get_restaurant_feedback_stats()
    assert stats['total_reviews'] == 2
    assert stats['average_service_rating'] == 4.0
    assert stats['average_ambiance_rating'] == 4.0
    assert stats['average_cleanliness_rating'] == 4.5
    assert stats['average_value_rating'] == 3.5

def test_get_recent_feedback(db_session: Session, rating_service: RatingService, test_user: User):
    # Create multiple feedback entries
    feedback_data_list = [
        RestaurantFeedbackCreate(
            feedback_text="Recent feedback",
            service_rating=5,
            ambiance_rating=4,
            cleanliness_rating=5,
            value_rating=4
        ),
        RestaurantFeedbackCreate(
            feedback_text="Older feedback",
            service_rating=3,
            ambiance_rating=4,
            cleanliness_rating=4,
            value_rating=3
        )
    ]
    
    for feedback_data in feedback_data_list:
        rating_service.create_restaurant_feedback(feedback_data, test_user.id)
    
    # Get recent feedback (limit to 1)
    recent_feedback = rating_service.get_recent_feedback(limit=1)
    assert len(recent_feedback) == 1
    assert recent_feedback[0].feedback_text == "Recent feedback"
