import pytest
from fastapi.testclient import TestClient
from backend.api.app import app
from backend.models.schemas.rating import MenuItemRatingCreate, RestaurantFeedbackCreate

client = TestClient(app)

def test_rate_menu_item(client, test_user_token, test_menu_item):
    """Test rating a menu item"""
    rating_data = {
        "rating": 4,
        "comment": "Great dish!"
    }

    response = client.post(
        f"/api/menu/items/{test_menu_item.id}/rate",
        json=rating_data,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["rating"] == 4
    assert data["comment"] == "Great dish!"

def test_duplicate_menu_item_rating(client, test_user_token, test_menu_item):
    """Test that a user cannot rate the same menu item twice"""
    rating_data = {
        "rating": 4,
        "comment": "First rating"
    }

    # First rating
    response = client.post(
        f"/api/menu/items/{test_menu_item.id}/rate",
        json=rating_data,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 201

    # Second rating
    response = client.post(
        f"/api/menu/items/{test_menu_item.id}/rate",
        json=rating_data,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 400  # Bad request - already rated

def test_get_menu_item_ratings(client, test_user_token, test_menu_item):
    """Test getting all ratings for a menu item"""
    # Create a rating first
    rating_data = {
        "rating": 4,
        "comment": "Test rating"
    }
    client.post(
        f"/api/menu/items/{test_menu_item.id}/rate",
        json=rating_data,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    # Get ratings
    response = client.get(f"/api/menu/items/{test_menu_item.id}/ratings")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["rating"] == 4
    assert data[0]["comment"] == "Test rating"

def test_update_menu_item_rating(client, test_user_token, test_menu_item):
    """Test updating a menu item rating"""
    # Create initial rating
    rating_data = {
        "rating": 3,
        "comment": "Initial rating"
    }
    response = client.post(
        f"/api/menu/items/{test_menu_item.id}/rate",
        json=rating_data,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 201
    rating_id = response.json()["id"]

    # Update rating
    updated_data = {
        "rating": 5,
        "comment": "Updated rating"
    }
    response = client.put(
        f"/api/menu/items/{test_menu_item.id}/ratings/{rating_id}",
        json=updated_data,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["rating"] == 5
    assert data["comment"] == "Updated rating"

def test_delete_menu_item_rating(client, test_user_token, test_menu_item):
    """Test deleting a menu item rating"""
    # Create a rating first
    rating_data = {
        "rating": 4,
        "comment": "To be deleted"
    }
    response = client.post(
        f"/api/menu/items/{test_menu_item.id}/rate",
        json=rating_data,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 201
    rating_id = response.json()["id"]

    # Delete rating
    response = client.delete(
        f"/api/menu/items/{test_menu_item.id}/ratings/{rating_id}",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 204

def test_create_restaurant_feedback(client, test_user_token):
    """Test creating restaurant feedback"""
    feedback_data = {
        "category": "SERVICE",
        "rating": 5,
        "comment": "Great service!"
    }

    response = client.post(
        "/api/feedback",
        json=feedback_data,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["category"] == "SERVICE"
    assert data["rating"] == 5
    assert data["comment"] == "Great service!"

def test_get_restaurant_feedback_by_category(client, test_user_token):
    """Test getting restaurant feedback by category"""
    # Create feedback first
    feedback_data = {
        "category": "FOOD",
        "rating": 4,
        "comment": "Good food"
    }
    client.post(
        "/api/feedback",
        json=feedback_data,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    # Get feedback by category
    response = client.get("/api/feedback/FOOD")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["category"] == "FOOD"
    assert data[0]["rating"] == 4
    assert data[0]["comment"] == "Good food"

def test_invalid_feedback_category(client, test_user_token):
    """Test creating feedback with invalid category"""
    feedback_data = {
        "category": "INVALID",
        "rating": 5,
        "comment": "Test feedback"
    }

    response = client.post(
        "/api/feedback",
        json=feedback_data,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 422  # Validation error
