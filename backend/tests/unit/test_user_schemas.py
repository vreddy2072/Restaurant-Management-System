import pytest
from datetime import datetime
from pydantic import ValidationError
from backend.models.schemas.user import UserCreate, UserUpdate, User, UserLogin

def test_user_create_valid():
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "strongpassword123",
        "first_name": "Test",
        "last_name": "User",
        "role": "customer",
        "phone_number": "+1234567890"
    }
    user = UserCreate(**user_data)
    assert user.username == user_data["username"]
    assert user.email == user_data["email"]
    assert user.password == user_data["password"]
    assert user.role == user_data["role"]

def test_user_create_invalid_email():
    user_data = {
        "username": "testuser",
        "email": "invalid-email",  # Invalid email format
        "password": "strongpassword123",
        "first_name": "Test",
        "last_name": "User",
        "role": "customer"
    }
    with pytest.raises(ValidationError):
        UserCreate(**user_data)

def test_user_create_invalid_role():
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "strongpassword123",
        "first_name": "Test",
        "last_name": "User",
        "role": "invalid_role"  # Invalid role
    }
    with pytest.raises(ValidationError):
        UserCreate(**user_data)

def test_user_create_invalid_phone():
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "strongpassword123",
        "first_name": "Test",
        "last_name": "User",
        "role": "customer",
        "phone_number": "123"  # Invalid phone number
    }
    with pytest.raises(ValidationError):
        UserCreate(**user_data)

def test_user_update_valid():
    user_data = {
        "username": "newusername",
        "email": "newemail@example.com",
        "phone_number": "+1987654321"
    }
    user = UserUpdate(**user_data)
    assert user.username == user_data["username"]
    assert user.email == user_data["email"]
    assert user.phone_number == user_data["phone_number"]

def test_user_update_partial():
    # UserUpdate should allow partial updates
    user = UserUpdate(username="newusername")
    assert user.username == "newusername"
    assert user.email is None
    assert user.phone_number is None

def test_user_response():
    user_data = {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "role": "customer",
        "is_active": True,
        "phone_number": "+1234567890",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    user = User(**user_data)
    assert user.id == user_data["id"]
    assert user.username == user_data["username"]
    assert user.email == user_data["email"]
    assert user.is_active == user_data["is_active"]

def test_user_login_valid():
    login_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    login = UserLogin(**login_data)
    assert login.email == login_data["email"]
    assert login.password == login_data["password"]

def test_user_login_invalid_email():
    login_data = {
        "email": "invalid-email",
        "password": "password123"
    }
    with pytest.raises(ValidationError):
        UserLogin(**login_data)
