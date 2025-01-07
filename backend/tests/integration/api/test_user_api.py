import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.api.app import app
from backend.models.schemas.user import UserCreate, UserUpdate
from backend.services.user_service import UserService

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
        json={
            "email": user_data["email"],
            "password": user_data["password"]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_invalid_login(client: TestClient, db_session: Session):
    """Test login with invalid credentials"""
    response = client.post(
        "/api/users/login",
        json={
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401

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
        json={
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

def test_deactivate_user(client: TestClient, db_session: Session):
    """Test deactivating user account"""
    # Create and login user
    user_data = {
        "username": "deactivateuser",
        "email": "deactivate@example.com",
        "password": "strongpass123",
        "first_name": "Deactivate",
        "last_name": "User",
        "role": "customer"
    }
    client.post("/api/users/register", json=user_data)

    login_response = client.post(
        "/api/users/login",
        json={
            "email": user_data["email"],
            "password": user_data["password"]
        }
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Deactivate account
    response = client.delete("/api/users/me", headers=headers)
    assert response.status_code == 204

    # Try to access account after deactivation
    response = client.get("/api/users/me", headers=headers)
    assert response.status_code == 401
    assert "Not authenticated or user is deactivated" in response.json()["detail"]

def test_guest_login(client: TestClient, db_session: Session):
    """Test guest user login functionality"""
    response = client.post("/api/users/guest-login")
    assert response.status_code == 200
    
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert "user" in data
    
    user = data["user"]
    assert user["is_guest"] is True
    assert user["role"] == "customer"
    assert user["username"].startswith("guest_")
    assert user["email"].endswith("@guest.local")

def test_guest_user_can_access_protected_routes(client: TestClient, db_session: Session):
    """Test that guest users can access protected routes"""
    # First create and login as guest
    login_response = client.post("/api/users/guest-login")
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    # Try to access protected route
    headers = {"Authorization": f"Bearer {token}"}
    me_response = client.get("/api/users/me", headers=headers)
    assert me_response.status_code == 200
    user_data = me_response.json()
    assert user_data["is_guest"] is True

def test_guest_user_update(client: TestClient, db_session: Session):
    """Test that guest users can update their information"""
    # First create and login as guest
    login_response = client.post("/api/users/guest-login")
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    # Update user info
    headers = {"Authorization": f"Bearer {token}"}
    update_data = {
        "first_name": "Updated",
        "last_name": "Guest"
    }
    update_response = client.put("/api/users/me", headers=headers, json=update_data)
    assert update_response.status_code == 200
    updated_user = update_response.json()
    assert updated_user["first_name"] == "Updated"
    assert updated_user["last_name"] == "Guest"
    assert updated_user["is_guest"] is True  # Ensure guest status is maintained

def test_guest_user_deactivation(client: TestClient, db_session: Session):
    """Test that guest users can deactivate their accounts"""
    # First create and login as guest
    login_response = client.post("/api/users/guest-login")
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Deactivate account
    headers = {"Authorization": f"Bearer {token}"}
    deactivate_response = client.delete("/api/users/me", headers=headers)
    assert deactivate_response.status_code == 204

    # Try to access protected route with deactivated account
    me_response = client.get("/api/users/me", headers=headers)
    assert me_response.status_code == 401
    assert "Not authenticated or user is deactivated" in me_response.json()["detail"]
