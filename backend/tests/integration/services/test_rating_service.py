import pytest
from sqlalchemy.exc import IntegrityError
from backend.services.rating_service import RatingService
from backend.models.schemas.rating import MenuItemRatingCreate, RestaurantFeedbackCreate

def test_create_menu_item_rating(db_session, test_user, sample_menu_item):
    service = RatingService(db_session)
    rating_data = MenuItemRatingCreate(
        menu_item_id=sample_menu_item.id,
        rating=4,
        comment="Great dish!"
    )
    
    rating = service.create_menu_item_rating(rating_data, test_user.id)
    assert rating.rating == 4
    assert rating.comment == "Great dish!"
    assert rating.user_id == test_user.id
    assert rating.menu_item_id == sample_menu_item.id

def test_duplicate_rating(db_session, test_user, sample_menu_item):
    service = RatingService(db_session)
    rating_data = MenuItemRatingCreate(
        menu_item_id=sample_menu_item.id,
        rating=4,
        comment="First rating"
    )
    
    service.create_menu_item_rating(rating_data, test_user.id)
    
    duplicate_rating = MenuItemRatingCreate(
        menu_item_id=sample_menu_item.id,
        rating=5,
        comment="Second rating"
    )
    
    with pytest.raises(ValueError, match="User has already rated this menu item"):
        service.create_menu_item_rating(duplicate_rating, test_user.id)

def test_get_menu_item_ratings(db_session, test_user, sample_menu_item):
    service = RatingService(db_session)
    rating_data = MenuItemRatingCreate(
        menu_item_id=sample_menu_item.id,
        rating=4,
        comment="Test rating"
    )
    
    service.create_menu_item_rating(rating_data, test_user.id)
    ratings = service.get_menu_item_ratings(sample_menu_item.id)
    
    assert len(ratings) == 1
    assert ratings[0].rating == 4
    assert ratings[0].comment == "Test rating"

def test_update_menu_item_rating(db_session, test_user, sample_menu_item):
    service = RatingService(db_session)
    rating_data = MenuItemRatingCreate(
        menu_item_id=sample_menu_item.id,
        rating=4,
        comment="Original rating"
    )
    
    service.create_menu_item_rating(rating_data, test_user.id)
    
    updated_rating = MenuItemRatingCreate(
        menu_item_id=sample_menu_item.id,
        rating=5,
        comment="Updated rating"
    )
    
    result = service.update_menu_item_rating(test_user.id, sample_menu_item.id, updated_rating)
    assert result.rating == 5
    assert result.comment == "Updated rating"

def test_delete_menu_item_rating(db_session, test_user, sample_menu_item):
    service = RatingService(db_session)
    rating_data = MenuItemRatingCreate(
        menu_item_id=sample_menu_item.id,
        rating=4,
        comment="Test rating"
    )
    
    service.create_menu_item_rating(rating_data, test_user.id)
    assert service.delete_menu_item_rating(test_user.id, sample_menu_item.id) is True
    assert service.get_user_menu_item_rating(test_user.id, sample_menu_item.id) is None

def test_create_restaurant_feedback(db_session, test_user):
    service = RatingService(db_session)
    feedback_data = RestaurantFeedbackCreate(
        feedback_text="Great service!",
        category="service"
    )
    
    feedback = service.create_restaurant_feedback(feedback_data, test_user.id)
    assert feedback.feedback_text == "Great service!"
    assert feedback.category == "service"
    assert feedback.user_id == test_user.id

def test_get_restaurant_feedback_by_category(db_session, test_user):
    service = RatingService(db_session)
    feedback_data1 = RestaurantFeedbackCreate(
        feedback_text="Great service!",
        category="service"
    )
    feedback_data2 = RestaurantFeedbackCreate(
        feedback_text="Delicious food!",
        category="food"
    )
    
    service.create_restaurant_feedback(feedback_data1, test_user.id)
    service.create_restaurant_feedback(feedback_data2, test_user.id)
    
    service_feedback = service.get_restaurant_feedback(category="service")
    assert len(service_feedback) == 1
    assert service_feedback[0].feedback_text == "Great service!"

def test_invalid_feedback_category(db_session, test_user):
    service = RatingService(db_session)
    with pytest.raises(ValueError, match="Invalid category"):
        service.get_restaurant_feedback(category="invalid_category")

def test_get_user_feedback(db_session, test_user):
    service = RatingService(db_session)
    feedback_data1 = RestaurantFeedbackCreate(
        feedback_text="Great service!",
        category="service"
    )
    feedback_data2 = RestaurantFeedbackCreate(
        feedback_text="Nice ambiance!",
        category="ambiance"
    )
    
    service.create_restaurant_feedback(feedback_data1, test_user.id)
    service.create_restaurant_feedback(feedback_data2, test_user.id)
    
    user_feedback = service.get_user_feedback(test_user.id)
    assert len(user_feedback) == 2
    categories = {feedback.category for feedback in user_feedback}
    assert categories == {"service", "ambiance"}
