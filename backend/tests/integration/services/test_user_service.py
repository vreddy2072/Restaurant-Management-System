import pytest
from datetime import datetime
from sqlalchemy.orm import Session

from backend.services.user_service import UserService
from backend.models.schemas.user import UserCreate, UserUpdate

def test_create_user(db_session: Session):
    service = UserService(db_session)
    user_data = UserCreate(
        username="testuser",
        email="test@example.com",
        password="strongpass123",
        first_name="Test",
        last_name="User",
        role="customer",
        phone_number="+1234567890"
    )
    
    user = service.create_user(user_data)
    assert user.username == user_data.username
    assert user.email == user_data.email
    assert user.first_name == user_data.first_name
    assert user.last_name == user_data.last_name
    assert user.role == user_data.role
    assert user.phone_number == user_data.phone_number
    assert user.is_active is True
    assert isinstance(user.created_at, datetime)

def test_create_duplicate_email(db_session: Session):
    service = UserService(db_session)
    user_data1 = UserCreate(
        username="user1",
        email="duplicate@example.com",
        password="strongpass123",
        first_name="First",
        last_name="User",
        role="customer"
    )
    service.create_user(user_data1)
    
    user_data2 = UserCreate(
        username="user2",
        email="duplicate@example.com",  # Same email
        password="strongpass123",
        first_name="Second",
        last_name="User",
        role="customer"
    )
    with pytest.raises(ValueError):
        service.create_user(user_data2)

def test_create_duplicate_username(db_session: Session):
    service = UserService(db_session)
    user_data1 = UserCreate(
        username="sameuser",
        email="first@example.com",
        password="strongpass123",
        first_name="First",
        last_name="User",
        role="customer"
    )
    service.create_user(user_data1)
    
    user_data2 = UserCreate(
        username="sameuser",  # Same username
        email="second@example.com",
        password="strongpass123",
        first_name="Second",
        last_name="User",
        role="customer"
    )
    with pytest.raises(ValueError):
        service.create_user(user_data2)

def test_get_user_by_email(db_session: Session):
    service = UserService(db_session)
    user_data = UserCreate(
        username="getuser",
        email="get@example.com",
        password="strongpass123",
        first_name="Get",
        last_name="User",
        role="customer"
    )
    created_user = service.create_user(user_data)
    
    found_user = service.get_user_by_email(user_data.email)
    assert found_user.id == created_user.id
    assert found_user.email == user_data.email

def test_authenticate_user(db_session: Session):
    service = UserService(db_session)
    user_data = UserCreate(
        username="authuser",
        email="auth@example.com",
        password="strongpass123",
        first_name="Auth",
        last_name="User",
        role="customer"
    )
    service.create_user(user_data)
    
    # Test successful authentication
    authenticated_user = service.authenticate_user(user_data.email, user_data.password)
    assert authenticated_user is not None
    assert authenticated_user.email == user_data.email
    
    # Test failed authentication
    assert service.authenticate_user(user_data.email, "wrongpass") is None
    assert service.authenticate_user("wrong@email.com", user_data.password) is None

def test_update_user(db_session: Session):
    service = UserService(db_session)
    user_data = UserCreate(
        username="updateuser",
        email="update@example.com",
        password="strongpass123",
        first_name="Update",
        last_name="User",
        role="customer"
    )
    user = service.create_user(user_data)
    
    update_data = UserUpdate(
        first_name="Updated",
        last_name="Name",
        phone_number="+9876543210"
    )
    updated_user = service.update_user(user.id, update_data)
    assert updated_user.first_name == update_data.first_name
    assert updated_user.last_name == update_data.last_name
    assert updated_user.phone_number == update_data.phone_number
    assert updated_user.email == user_data.email  # Unchanged

def test_update_user_email(db_session: Session):
    service = UserService(db_session)
    user_data = UserCreate(
        username="emailupdate",
        email="old@example.com",
        password="strongpass123",
        first_name="Email",
        last_name="Update",
        role="customer"
    )
    user = service.create_user(user_data)
    
    # Create another user to test email uniqueness
    other_user_data = UserCreate(
        username="otheruser",
        email="other@example.com",
        password="strongpass123",
        first_name="Other",
        last_name="User",
        role="customer"
    )
    other_user = service.create_user(other_user_data)
    
    # Try to update to existing email
    with pytest.raises(ValueError):
        service.update_user(user.id, UserUpdate(email=other_user_data.email))

def test_deactivate_user(db_session: Session):
    service = UserService(db_session)
    user_data = UserCreate(
        username="deactiveuser",
        email="deactive@example.com",
        password="strongpass123",
        first_name="Deactive",
        last_name="User",
        role="customer"
    )
    user = service.create_user(user_data)
    
    service.deactivate_user(user.id)
    deactivated_user = service.get_user_by_email(user_data.email)
    assert deactivated_user.is_active is False

# Guest User Tests
def test_create_guest_user(db_session: Session):
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

def test_authenticate_guest(db_session: Session):
    """Test guest user authentication"""
    service = UserService(db_session)
    guest_user, password = service.authenticate_guest()

    assert guest_user.id is not None
    assert guest_user.is_guest is True
    assert len(password) == 8  # UUID4 truncated to 8 chars
    assert guest_user.username.endswith(password)  # Password is part of username

def test_guest_user_unique_credentials(db_session: Session):
    """Test that each guest user gets unique credentials"""
    service = UserService(db_session)
    guest1 = service.create_guest_user()
    guest2 = service.create_guest_user()

    assert guest1.username != guest2.username
    assert guest1.email != guest2.email
    assert guest1.password_hash != guest2.password_hash

def test_guest_user_format(db_session: Session):
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
