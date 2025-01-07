import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import time

from backend.models.orm.user import User
from backend.models.schemas.rating import RestaurantFeedbackCreate

def test_create_restaurant_feedback(client: TestClient, test_user_token: str):
    """Test creating restaurant feedback."""
    feedback_data = {
        "feedback_text": "Great experience overall!",
        "service_rating": 5,
        "ambiance_rating": 4,
        "cleanliness_rating": 5,
        "value_rating": 4
    }
    headers = {"Authorization": f"Bearer {test_user_token}"}
    response = client.post("/api/ratings/restaurant-feedback", json=feedback_data, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["feedback_text"] == feedback_data["feedback_text"]
    assert data["service_rating"] == feedback_data["service_rating"]
    assert data["ambiance_rating"] == feedback_data["ambiance_rating"]
    assert data["cleanliness_rating"] == feedback_data["cleanliness_rating"]
    assert data["value_rating"] == feedback_data["value_rating"]

def test_create_restaurant_feedback_invalid(client: TestClient, test_user_token: str):
    """Test creating restaurant feedback with invalid data."""
    # Test invalid rating value
    feedback_data = {
        "feedback_text": "Test feedback",
        "service_rating": 6,  # Invalid: greater than 5
        "ambiance_rating": 4,
        "cleanliness_rating": 5,
        "value_rating": 4
    }
    headers = {"Authorization": f"Bearer {test_user_token}"}
    response = client.post("/api/ratings/restaurant-feedback", json=feedback_data, headers=headers)
    assert response.status_code == 422

    # Test empty feedback text
    feedback_data["service_rating"] = 5
    feedback_data["feedback_text"] = ""
    response = client.post("/api/ratings/restaurant-feedback", json=feedback_data, headers=headers)
    assert response.status_code == 422

def test_get_restaurant_feedback(client: TestClient, test_user_token: str):
    """Test getting all restaurant feedback."""
    # First create some feedback
    feedback_data = {
        "feedback_text": "Test feedback",
        "service_rating": 5,
        "ambiance_rating": 4,
        "cleanliness_rating": 5,
        "value_rating": 4
    }
    headers = {"Authorization": f"Bearer {test_user_token}"}
    client.post("/api/ratings/restaurant-feedback", json=feedback_data, headers=headers)

    # Get all feedback
    response = client.get("/api/ratings/restaurant-feedback", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert isinstance(data, list)

def test_get_user_feedback(client: TestClient, test_user_token: str):
    """Test getting user's feedback."""
    # First create feedback
    feedback_data = {
        "feedback_text": "User's feedback",
        "service_rating": 5,
        "ambiance_rating": 4,
        "cleanliness_rating": 5,
        "value_rating": 4
    }
    headers = {"Authorization": f"Bearer {test_user_token}"}
    client.post("/api/ratings/restaurant-feedback", json=feedback_data, headers=headers)

    # Get user's feedback
    response = client.get("/api/ratings/restaurant-feedback/user", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["feedback_text"] == feedback_data["feedback_text"]

def test_get_restaurant_feedback_stats(client: TestClient, test_user_token: str):
    """Test getting restaurant feedback statistics."""
    # First create some feedback
    feedback_data_list = [
        {
            "feedback_text": "Great service!",
            "service_rating": 5,
            "ambiance_rating": 4,
            "cleanliness_rating": 5,
            "value_rating": 4
        },
        {
            "feedback_text": "Good food but slow service",
            "service_rating": 3,
            "ambiance_rating": 4,
            "cleanliness_rating": 4,
            "value_rating": 3
        }
    ]
    headers = {"Authorization": f"Bearer {test_user_token}"}
    for feedback_data in feedback_data_list:
        client.post("/api/ratings/restaurant-feedback", json=feedback_data, headers=headers)

    # Get feedback stats
    response = client.get("/api/ratings/restaurant-feedback/stats", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_reviews" in data
    assert "average_service_rating" in data
    assert "average_ambiance_rating" in data
    assert "average_cleanliness_rating" in data
    assert "average_value_rating" in data

def test_get_recent_feedback(client: TestClient, test_user_token: str):
    """Test getting recent feedback."""
    # First create some feedback
    feedback_data_list = [
        {
            "feedback_text": "Recent feedback",
            "service_rating": 5,
            "ambiance_rating": 4,
            "cleanliness_rating": 5,
            "value_rating": 4
        },
        {
            "feedback_text": "Older feedback",
            "service_rating": 3,
            "ambiance_rating": 4,
            "cleanliness_rating": 4,
            "value_rating": 3
        }
    ]
    headers = {"Authorization": f"Bearer {test_user_token}"}
    for feedback_data in feedback_data_list:
        client.post("/api/ratings/restaurant-feedback", json=feedback_data, headers=headers)
        time.sleep(0.1)  # Add a small delay between feedback entries

    # Get recent feedback
    response = client.get("/api/ratings/restaurant-feedback/recent", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["feedback_text"] == "Older feedback"  # The last entry should be the most recent
    assert data[1]["feedback_text"] == "Recent feedback"  # The first entry should be older

def test_unauthorized_access(client: TestClient):
    """Test accessing endpoints without authentication."""
    feedback_data = {
        "feedback_text": "Test feedback",
        "service_rating": 5,
        "ambiance_rating": 4,
        "cleanliness_rating": 5,
        "value_rating": 4
    }

    # Try to create feedback without token
    response = client.post("/api/ratings/restaurant-feedback", json=feedback_data)
    assert response.status_code == 401

    # Try to get feedback without token
    response = client.get("/api/ratings/restaurant-feedback")
    assert response.status_code == 401

    # Try to get user feedback without token
    response = client.get("/api/ratings/restaurant-feedback/user")
    assert response.status_code == 401

    # Try to get feedback stats without token
    response = client.get("/api/ratings/restaurant-feedback/stats")
    assert response.status_code == 401

    # Try to get recent feedback without token
    response = client.get("/api/ratings/restaurant-feedback/recent")
    assert response.status_code == 401 