import pytest
from datetime import datetime, timedelta
from backend.services.user_service import UserService
from backend.models.schemas.user import UserCreate, UserLogin
from backend.models.orm.user import User
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import asyncio

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def test_create_user(db_session):
    """Test user creation through user service"""
    user_service = UserService(db_session)
    user_data = UserCreate(
        username="servicetest",
        email="service@example.com",
        password="testpassword",
        first_name="Service",
        last_name="Test",
        role="customer"
    )
    user = user_service.create_user(user_data)
    assert user.email == "service@example.com"
    assert user.username == "servicetest"
    assert user.is_active is True

def test_authenticate_user(db_session):
    """Test user authentication through user service"""
    user_service = UserService(db_session)

    # Create a user first
    user_data = UserCreate(
        username="authtest",
        email="auth@example.com",
        password="testpassword",
        first_name="Auth",
        last_name="Test",
        role="customer"
    )
    user = user_service.create_user(user_data)

    # Test valid authentication
    authenticated_user = user_service.authenticate_user("auth@example.com", "testpassword")
    assert authenticated_user is not None
    assert authenticated_user.id == user.id

    # Test invalid password
    assert user_service.authenticate_user("auth@example.com", "wrongpassword") is None

    # Test invalid email
    assert user_service.authenticate_user("wrong@example.com", "testpassword") is None

def test_create_access_token(db_session):
    """Test access token creation"""
    user_service = UserService(db_session)

    # Create a user
    user_data = UserCreate(
        username="tokentest",
        email="token@example.com",
        password="testpassword",
        first_name="Token",
        last_name="Test",
        role="customer"
    )
    user = user_service.create_user(user_data)

    # Create a token
    from backend.utils.auth import create_access_token
    token = create_access_token(data={"sub": user.email})
    assert token is not None

@pytest.mark.asyncio
async def test_get_current_user(db_session):
    """Test getting current user from token"""
    user_service = UserService(db_session)

    # Create a user
    user_data = UserCreate(
        username="currentuser",
        email="current@example.com",
        password="testpassword",
        first_name="Current",
        last_name="Test",
        role="customer"
    )
    user = user_service.create_user(user_data)

    # Create a token
    from backend.utils.auth import create_access_token, get_current_user
    token = create_access_token(data={"sub": user.email})

    # Get current user from token
    current_user = await get_current_user(token, db_session)
    assert current_user.id == user.id
    assert current_user.email == user.email
