import pytest
from fastapi.testclient import TestClient
from backend.api.app import app
from backend.models.schemas.rating import MenuItemRatingCreate, RestaurantFeedbackCreate

client = TestClient(app)

def test_rate_menu_item(client, test_user_token, sample_menu_item):
    """Test rating a menu item"""
    rating_data = {
        "menu_item_id": sample_menu_item.id,
        "rating": 4,
        "comment": "Great dish!"
    }

    response = client.post(
        f"/api/ratings/menu-items/{sample_menu_item.id}",
        json=rating_data,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["rating"] == 4
    assert data["comment"] == "Great dish!"

def test_duplicate_menu_item_rating(client, test_user_token, sample_menu_item):
    """Test that a user cannot rate the same menu item twice"""
    rating_data = {
        "menu_item_id": sample_menu_item.id,
        "rating": 4,
        "comment": "First rating"
    }

    # First rating
    response = client.post(
        f"/api/ratings/menu-items/{sample_menu_item.id}",
        json=rating_data,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200

    # Second rating should update the first one
    updated_data = {
        "menu_item_id": sample_menu_item.id,
        "rating": 5,
        "comment": "Updated rating"
    }
    response = client.post(
        f"/api/ratings/menu-items/{sample_menu_item.id}",
        json=updated_data,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["rating"] == 5
    assert data["comment"] == "Updated rating"

def test_get_menu_item_ratings(client, test_user_token, sample_menu_item):
    """Test getting all ratings for a menu item"""
    # Create a rating first
    rating_data = {
        "menu_item_id": sample_menu_item.id,
        "rating": 4,
        "comment": "Test rating"
    }
    client.post(
        f"/api/ratings/menu-items/{sample_menu_item.id}",
        json=rating_data,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    # Get ratings
    response = client.get(f"/api/ratings/menu-items/{sample_menu_item.id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["rating"] == 4
    assert data[0]["comment"] == "Test rating"

def test_get_user_menu_item_rating(client, test_user_token, sample_menu_item):
    """Test getting user's rating for a menu item"""
    # Create a rating first
    rating_data = {
        "menu_item_id": sample_menu_item.id,
        "rating": 4,
        "comment": "User's rating"
    }
    client.post(
        f"/api/ratings/menu-items/{sample_menu_item.id}",
        json=rating_data,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    # Get user's rating
    response = client.get(
        f"/api/ratings/menu-items/{sample_menu_item.id}/user",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["rating"] == 4
    assert data["comment"] == "User's rating"

def test_delete_menu_item_rating(client, test_user_token, sample_menu_item):
    """Test deleting a menu item rating"""
    # Create a rating first
    rating_data = {
        "menu_item_id": sample_menu_item.id,
        "rating": 4,
        "comment": "To be deleted"
    }
    client.post(
        f"/api/ratings/menu-items/{sample_menu_item.id}",
        json=rating_data,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    # Delete rating
    response = client.delete(
        f"/api/ratings/menu-items/{sample_menu_item.id}",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 204

    # Verify rating is deleted
    response = client.get(
        f"/api/ratings/menu-items/{sample_menu_item.id}/user",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 404

def test_create_restaurant_feedback(client, test_user_token):
    """Test creating restaurant feedback"""
    feedback_data = {
        "feedback_text": "Great service!",
        "service_rating": 5,
        "ambiance_rating": 4,
        "cleanliness_rating": 5,
        "value_rating": 4
    }

    response = client.post(
        "/api/ratings/restaurant-feedback",
        json=feedback_data,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["feedback_text"] == "Great service!"
    assert data["service_rating"] == 5
    assert data["ambiance_rating"] == 4
    assert data["cleanliness_rating"] == 5
    assert data["value_rating"] == 4

def test_get_restaurant_feedback_by_category(client, test_user_token):
    """Test getting restaurant feedback by category"""
    # Create feedback first
    feedback_data = {
        "feedback_text": "Good food",
        "service_rating": 4,
        "ambiance_rating": 4,
        "cleanliness_rating": 4,
        "value_rating": 4
    }
    client.post(
        "/api/ratings/restaurant-feedback",
        json=feedback_data,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    # Get feedback by category
    response = client.get("/api/ratings/restaurant-feedback", headers={"Authorization": f"Bearer {test_user_token}"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["feedback_text"] == "Good food"
    assert data[0]["service_rating"] == 4

def test_invalid_feedback_category(client, test_user_token):
    """Test creating feedback with invalid category"""
    feedback_data = {
        "feedback_text": "Test feedback",
        "service_rating": 6,  # Invalid rating (should be 1-5)
        "ambiance_rating": 4,
        "cleanliness_rating": 5,
        "value_rating": 4
    }

    response = client.post(
        "/api/ratings/restaurant-feedback",
        json=feedback_data,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 422  # Validation error
