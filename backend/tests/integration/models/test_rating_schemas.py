import pytest
from datetime import datetime
from pydantic import ValidationError

from backend.models.schemas.rating import (
    RestaurantFeedbackBase,
    RestaurantFeedbackCreate,
    RestaurantFeedback,
    RestaurantFeedbackResponse,
    RestaurantFeedbackStats
)

def test_restaurant_feedback_base_valid():
    feedback = RestaurantFeedbackBase(
        feedback_text="Great experience!",
        service_rating=5,
        ambiance_rating=4,
        cleanliness_rating=5,
        value_rating=4
    )
    assert feedback.feedback_text == "Great experience!"
    assert feedback.service_rating == 5
    assert feedback.ambiance_rating == 4
    assert feedback.cleanliness_rating == 5
    assert feedback.value_rating == 4

def test_restaurant_feedback_base_invalid_ratings():
    # Test rating too low
    with pytest.raises(ValidationError) as exc_info:
        RestaurantFeedbackBase(
            feedback_text="Test",
            service_rating=0,  # Invalid: less than 1
            ambiance_rating=3,
            cleanliness_rating=3,
            value_rating=3
        )
    assert "Input should be greater than or equal to 1" in str(exc_info.value)

    # Test rating too high
    with pytest.raises(ValidationError) as exc_info:
        RestaurantFeedbackBase(
            feedback_text="Test",
            service_rating=3,
            ambiance_rating=6,  # Invalid: greater than 5
            cleanliness_rating=3,
            value_rating=3
        )
    assert "Input should be less than or equal to 5" in str(exc_info.value)

def test_restaurant_feedback_base_invalid_text():
    # Test empty feedback text
    with pytest.raises(ValidationError) as exc_info:
        RestaurantFeedbackBase(
            feedback_text="",
            service_rating=3,
            ambiance_rating=3,
            cleanliness_rating=3,
            value_rating=3
        )
    assert "String should have at least 1 character" in str(exc_info.value)

    # Test too long feedback text
    with pytest.raises(ValidationError) as exc_info:
        RestaurantFeedbackBase(
            feedback_text="a" * 1001,  # 1001 characters
            service_rating=3,
            ambiance_rating=3,
            cleanliness_rating=3,
            value_rating=3
        )
    assert "String should have at most 1000 characters" in str(exc_info.value)

def test_restaurant_feedback_response():
    now = datetime.utcnow()
    feedback = RestaurantFeedbackResponse(
        id=1,
        user_id=1,
        feedback_text="Great experience!",
        service_rating=5,
        ambiance_rating=4,
        cleanliness_rating=5,
        value_rating=4,
        created_at=now,
        updated_at=now
    )
    assert feedback.id == 1
    assert feedback.user_id == 1
    assert feedback.feedback_text == "Great experience!"
    assert feedback.service_rating == 5
    assert feedback.created_at == now
    assert feedback.updated_at == now

def test_restaurant_feedback_stats():
    stats = RestaurantFeedbackStats(
        average_service_rating=4.5,
        average_ambiance_rating=4.2,
        average_cleanliness_rating=4.8,
        average_value_rating=4.0,
        total_reviews=100
    )
    assert stats.average_service_rating == 4.5
    assert stats.average_ambiance_rating == 4.2
    assert stats.average_cleanliness_rating == 4.8
    assert stats.average_value_rating == 4.0
    assert stats.total_reviews == 100

def test_restaurant_feedback_stats_invalid():
    # Test invalid average ratings
    with pytest.raises(ValidationError) as exc_info:
        RestaurantFeedbackStats(
            average_service_rating=5.5,  # Invalid: greater than 5
            average_ambiance_rating=4.0,
            average_cleanliness_rating=4.0,
            average_value_rating=4.0,
            total_reviews=100
        )
    assert "Input should be less than or equal to 5" in str(exc_info.value)

    # Test negative total reviews
    with pytest.raises(ValidationError) as exc_info:
        RestaurantFeedbackStats(
            average_service_rating=4.0,
            average_ambiance_rating=4.0,
            average_cleanliness_rating=4.0,
            average_value_rating=4.0,
            total_reviews=-1  # Invalid: less than 0
        )
    assert "Input should be greater than or equal to 0" in str(exc_info.value) 