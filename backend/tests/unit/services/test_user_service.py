import pytest
from datetime import datetime
from backend.services.user_service import UserService
from backend.models.schemas.user import UserCreate

def test_create_guest_user(db_session):
    """Test creating a guest user"""
    service = UserService(db_session)
    guest_user = service.create_guest_user()

    assert guest_user.id is not None
    assert guest_user.is_guest is True
    assert guest_user.role == "customer"
    assert guest_user.username.startswith("guest_")
    assert guest_user.email.endswith("@guest.local")
    assert guest_user.first_name == "Guest"
    assert guest_user.last_name == "User"
    assert guest_user.is_active is True
    assert isinstance(guest_user.created_at, datetime)
    assert isinstance(guest_user.updated_at, datetime)

def test_authenticate_guest(db_session):
    """Test guest user authentication"""
    service = UserService(db_session)
    guest_user, password = service.authenticate_guest()

    assert guest_user.id is not None
    assert guest_user.is_guest is True
    assert len(password) == 8  # UUID4 truncated to 8 chars
    assert guest_user.username.endswith(password)  # Password is part of username

def test_guest_user_unique_credentials(db_session):
    """Test that each guest user gets unique credentials"""
    service = UserService(db_session)
    guest1 = service.create_guest_user()
    guest2 = service.create_guest_user()

    assert guest1.username != guest2.username
    assert guest1.email != guest2.email
    assert guest1.password_hash != guest2.password_hash

def test_guest_user_format(db_session):
    """Test the format of guest user credentials"""
    service = UserService(db_session)
    guest = service.create_guest_user()

    # Check username format (guest_YYYYMMDDHHMMSS_UUID)
    username_parts = guest.username.split('_')
    assert len(username_parts) == 3
    assert username_parts[0] == "guest"
    assert len(username_parts[1]) == 14  # YYYYMMDDHHMMSS
    assert len(username_parts[2]) == 8   # UUID4 truncated

    # Check email format
    assert guest.email == f"{guest.username}@guest.local"
