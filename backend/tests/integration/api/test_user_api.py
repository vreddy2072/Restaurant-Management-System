import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.api.app import app
from backend.models.schemas.user import UserCreate, UserUpdate
from backend.services.user import UserService

def test_register_user(client: TestClient, db_session: Session):
    """Test user registration endpoint"""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "strongpass123",
        "first_name": "Test",
        "last_name": "User",
        "role": "customer"
    }
    response = client.post("/api/users/register", json=user_data)
    print(f"Response content: {response.content}")  # Add this line for debugging
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]
    assert "password" not in data

def test_register_duplicate_email(client: TestClient, db_session: Session):
    """Test registration with duplicate email"""
    user_data = {
        "username": "firstuser",
        "email": "duplicate@example.com",
        "password": "strongpass123",
        "first_name": "First",
        "last_name": "User",
        "role": "customer"
    }
    # Register first user
    client.post("/api/users/register", json=user_data)

    # Try to register second user with same email
    user_data["username"] = "seconduser"
    response = client.post("/api/users/register", json=user_data)
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]

def test_login_user(client: TestClient, db_session: Session):
    """Test user login endpoint"""
    # Register user first
    user_data = {
        "username": "loginuser",
        "email": "login@example.com",
        "password": "strongpass123",
        "first_name": "Login",
        "last_name": "User",
        "role": "customer"
    }
    client.post("/api/users/register", json=user_data)

    # Try to login
    response = client.post(
        "/api/users/login",
        data={
            "email": user_data["email"],
            "password": user_data["password"]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_get_current_user(client: TestClient, db_session: Session):
    """Test getting current user info"""
    # Create and login user
    user_data = {
        "username": "currentuser",
        "email": "current@example.com",
        "password": "strongpass123",
        "first_name": "Current",
        "last_name": "User",
        "role": "customer"
    }
    client.post("/api/users/register", json=user_data)

    login_response = client.post(
        "/api/users/login",
        data={
            "email": user_data["email"],
            "password": user_data["password"]
        }
    )
    token = login_response.json()["access_token"]

    # Get current user info
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/users/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]

def test_update_user(client: TestClient, db_session: Session):
    """Test updating user info"""
    # Create and login user
    user_data = {
        "username": "updateuser",
        "email": "update@example.com",
        "password": "strongpass123",
        "first_name": "Update",
        "last_name": "User",
        "role": "customer"
    }
    client.post("/api/users/register", json=user_data)

    login_response = client.post(
        "/api/users/login",
        data={
            "email": user_data["email"],
            "password": user_data["password"]
        }
    )
    token = login_response.json()["access_token"]

    # Update user info
    headers = {"Authorization": f"Bearer {token}"}
    update_data = {
        "first_name": "Updated",
        "last_name": "Name"
    }
    response = client.put("/api/users/me", json=update_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == update_data["first_name"]
    assert data["last_name"] == update_data["last_name"]

def test_deactivate_user(client: TestClient, db_session: Session):
    """Test deactivating user account"""
    # Create and login user
    user_data = {
        "username": "deactiveuser",
        "email": "deactive@example.com",
        "password": "strongpass123",
        "first_name": "Deactive",
        "last_name": "User",
        "role": "customer"
    }
    client.post("/api/users/register", json=user_data)

    login_response = client.post(
        "/api/users/login",
        data={
            "email": user_data["email"],
            "password": user_data["password"]
        }
    )
    token = login_response.json()["access_token"]

    # Deactivate account
    headers = {"Authorization": f"Bearer {token}"}
    response = client.delete("/api/users/me", headers=headers)
    assert response.status_code == 204

    # Try to login after deactivation
    login_response = client.post(
        "/api/users/login",
        data={
            "email": user_data["email"],
            "password": user_data["password"]
        }
    )
    assert login_response.status_code == 401
