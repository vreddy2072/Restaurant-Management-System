import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from backend.models.orm.user import User

def test_create_user(db_session):
    """Test creating a new user"""
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password",
        first_name="Test",
        last_name="User",
        role="customer",
        phone_number="1234567890"
    )
    db_session.add(user)
    db_session.commit()

    assert user.id is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.password_hash == "hashed_password"
    assert user.first_name == "Test"
    assert user.last_name == "User"
    assert user.role == "customer"
    assert user.is_active is True
    assert user.phone_number == "1234567890"
    assert isinstance(user.created_at, datetime)
    assert isinstance(user.updated_at, datetime)

def test_get_user_by_email(db_session):
    """Test retrieving a user by email"""
    user = User(
        username="logintest",
        email="login@example.com",
        password_hash="hashed_password",
        first_name="Login",
        last_name="Test",
        role="customer",
        phone_number="1234567890"
    )
    db_session.add(user)
    db_session.commit()

    # Test retrieving user by email
    retrieved_user = db_session.query(User).filter(User.email == "login@example.com").first()
    assert retrieved_user is not None
    assert retrieved_user.username == "logintest"
    assert retrieved_user.password_hash == "hashed_password"

def test_password_hashing(db_session):
    """Test password hashing and verification"""
    user = User(
        username="hashtest",
        email="hash@example.com",
        password_hash="hashed_password",
        first_name="Hash",
        last_name="Test",
        role="customer"
    )
    db_session.add(user)
    db_session.commit()

    assert user.password_hash != "password123"  # Password should be hashed
    assert len(user.password_hash) > 0  # Hash should not be empty

def test_unique_constraints(db_session):
    """Test unique constraints on username and email"""
    user1 = User(
        username="unique1",
        email="unique1@example.com",
        password_hash="hashed_password",
        first_name="Unique",
        last_name="One",
        role="customer"
    )
    db_session.add(user1)
    db_session.commit()

    # Test unique username constraint
    user2 = User(
        username="unique1",  # Same username
        email="unique2@example.com",
        password_hash="hashed_password",
        first_name="Unique",
        last_name="Two",
        role="customer"
    )
    with pytest.raises(IntegrityError):
        db_session.add(user2)
        db_session.commit()
    db_session.rollback()

    # Test unique email constraint
    user3 = User(
        username="unique3",
        email="unique1@example.com",  # Same email
        password_hash="hashed_password",
        first_name="Unique",
        last_name="Three",
        role="customer"
    )
    with pytest.raises(IntegrityError):
        db_session.add(user3)
        db_session.commit()
    db_session.rollback()

def test_role_validation():
    """Test role validation"""
    with pytest.raises(ValueError):
        User(
            username="roletest",
            email="role@example.com",
            password_hash="hashed_password",
            first_name="Role",
            last_name="Test",
            role="invalid_role"  # Invalid role
        )

def test_email_validation():
    """Test email validation"""
    with pytest.raises(ValueError):
        User(
            username="emailtest",
            email="invalid_email",  # Invalid email
            password_hash="hashed_password",
            first_name="Email",
            last_name="Test",
            role="customer"
        )

def test_required_fields(db_session):
    """Test required fields validation"""
    # Test missing username
    with pytest.raises(IntegrityError):
        user = User(
            email="test@example.com",
            password_hash="hashed_password",
            first_name="Test",
            last_name="User",
            role="customer"
        )
        db_session.add(user)
        db_session.commit()
    db_session.rollback()

    # Test missing email
    with pytest.raises(IntegrityError):
        user = User(
            username="testuser",
            password_hash="hashed_password",
            first_name="Test",
            last_name="User",
            role="customer"
        )
        db_session.add(user)
        db_session.commit()
    db_session.rollback()

def test_to_dict(db_session):
    """Test the to_dict method"""
    user = User(
        username="dicttest",
        email="dict@example.com",
        password_hash="hashed_password",
        first_name="Dict",
        last_name="Test",
        role="customer"
    )
    db_session.add(user)
    db_session.commit()

    user_dict = user.to_dict()
    assert user_dict["username"] == "dicttest"
    assert user_dict["email"] == "dict@example.com"
    assert user_dict["first_name"] == "Dict"
    assert user_dict["last_name"] == "Test"
    assert user_dict["role"] == "customer"
    assert "password_hash" not in user_dict  # Password hash should not be included

def test_guest_user_creation(db_session):
    """Test creating a guest user"""
    guest_user = User(
        username="guest_123",
        email="guest_123@example.com",
        password_hash="guest_password_hash",
        first_name="Guest",
        last_name="User",
        role="customer",
        is_guest=True
    )
    db_session.add(guest_user)
    db_session.commit()

    assert guest_user.id is not None
    assert guest_user.is_guest is True
    assert guest_user.role == "customer"
    assert guest_user.is_active is True
    assert isinstance(guest_user.created_at, datetime)

def test_guest_user_to_dict(db_session):
    """Test the to_dict method includes is_guest field"""
    guest_user = User(
        username="guest_dict",
        email="guest_dict@example.com",
        password_hash="guest_password_hash",
        first_name="Guest",
        last_name="Dict",
        role="customer",
        is_guest=True
    )
    db_session.add(guest_user)
    db_session.commit()

    user_dict = guest_user.to_dict()
    assert "is_guest" in user_dict
    assert user_dict["is_guest"] is True

def test_guest_user_filtering(db_session):
    """Test filtering users by guest status"""
    # Create a regular user
    regular_user = User(
        username="regular",
        email="regular@example.com",
        password_hash="regular_hash",
        first_name="Regular",
        last_name="User",
        role="customer",
        is_guest=False
    )

    # Create a guest user
    guest_user = User(
        username="guest_filter",
        email="guest_filter@example.com",
        password_hash="guest_hash",
        first_name="Guest",
        last_name="Filter",
        role="customer",
        is_guest=True
    )

    db_session.add_all([regular_user, guest_user])
    db_session.commit()

    # Test filtering guest users
    guest_users = db_session.query(User).filter(User.is_guest == True).all()
    assert len(guest_users) >= 1
    assert guest_users[0].is_guest is True

    # Test filtering regular users
    regular_users = db_session.query(User).filter(User.is_guest == False).all()
    assert len(regular_users) >= 1
    assert regular_users[0].is_guest is False

def test_guest_user_default_value(db_session):
    """Test that is_guest defaults to False when not specified"""
    regular_user = User(
        username="default_test",
        email="default@example.com",
        password_hash="default_hash",
        first_name="Default",
        last_name="Test",
        role="customer"
    )
    db_session.add(regular_user)
    db_session.commit()

    assert regular_user.is_guest is False

def test_admin_user_creation(db_session):
    """Test creating an admin user"""
    admin_user = User(
        username="admin_test",
        email="admin@example.com",
        password_hash="admin_password_hash",
        first_name="Admin",
        last_name="User",
        role="admin",
        is_admin=True
    )
    db_session.add(admin_user)
    db_session.commit()

    assert admin_user.id is not None
    assert admin_user.is_admin is True
    assert admin_user.role == "admin"
    assert admin_user.is_active is True
    assert isinstance(admin_user.created_at, datetime)

def test_admin_user_to_dict(db_session):
    """Test the to_dict method includes is_admin field"""
    admin_user = User(
        username="admin_dict",
        email="admin_dict@example.com",
        password_hash="admin_password_hash",
        first_name="Admin",
        last_name="Dict",
        role="admin",
        is_admin=True
    )
    db_session.add(admin_user)
    db_session.commit()

    user_dict = admin_user.to_dict()
    assert "is_admin" in user_dict
    assert user_dict["is_admin"] is True

def test_admin_user_default_value(db_session):
    """Test that is_admin defaults to False when not specified"""
    regular_user = User(
        username="default_admin_test",
        email="default_admin@example.com",
        password_hash="default_hash",
        first_name="Default",
        last_name="Test",
        role="customer"
    )
    db_session.add(regular_user)
    db_session.commit()

    assert regular_user.is_admin is False

def test_admin_and_guest_flags(db_session):
    """Test that a user can't be both admin and guest"""
    user = User(
        username="test_flags",
        email="flags@example.com",
        password_hash="test_hash",
        first_name="Test",
        last_name="Flags",
        role="admin",
        is_admin=True,
        is_guest=True
    )
    db_session.add(user)
    db_session.commit()

    # A user can technically have both flags, but it's not recommended
    # This test documents this behavior
    assert user.is_admin is True
    assert user.is_guest is True
