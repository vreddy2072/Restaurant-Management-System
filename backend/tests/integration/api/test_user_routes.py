import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.api.app import app
from backend.models.schemas.user import UserCreate

client = TestClient(app)

def test_create_user():
    """Test user creation endpoint"""
    response = client.post(
        "/api/users/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword",
            "first_name": "Test",
            "last_name": "User",
            "role": "customer"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"
    assert "password" not in data

def test_get_user():
    """Test getting user details"""
    # First create a user
    create_response = client.post(
        "/api/users/register",
        json={
            "username": "getuser",
            "email": "get@example.com",
            "password": "testpassword",
            "first_name": "Get",
            "last_name": "User",
            "role": "customer"
        }
    )
    assert create_response.status_code == 201
    user_id = create_response.json()["id"]

    # Login as the user
    login_response = client.post(
        "/api/users/login",
        data={
            "email": "get@example.com",
            "password": "testpassword"
        }
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Get user details
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/users/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "get@example.com"
    assert data["username"] == "getuser"

def test_login_user():
    """Test user login endpoint"""
    # First create a user
    client.post(
        "/api/users/register",
        json={
            "username": "loginuser",
            "email": "login@example.com",
            "password": "testpassword",
            "first_name": "Login",
            "last_name": "User",
            "role": "customer"
        }
    )

    # Try to login
    response = client.post(
        "/api/users/login",
        data={
            "email": "login@example.com",
            "password": "testpassword"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_invalid_login():
    """Test login with invalid credentials"""
    response = client.post(
        "/api/users/login",
        data={
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401
    assert "detail" in response.json()
