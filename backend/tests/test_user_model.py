import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from app.models.user import User
from utils.database import SessionLocal, init_db
import subprocess
import os
from alembic import command
from alembic.config import Config

@pytest.fixture(scope="session", autouse=True)
def initialize_database():
    """Initialize the database before running tests"""
    # Run alembic migrations
    subprocess.run(["alembic", "upgrade", "head"], cwd=os.path.dirname(os.path.dirname(__file__)))
    init_db()

@pytest.fixture
def db_session():
    """Get a database session for each test"""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()

def test_create_user(db_session):
    """Test creating a new user"""
    user = User(
        username='testuser',
        email='test@example.com',
        first_name='Test',
        last_name='User',
        role='customer',
        is_active=True
    )
    user.set_password('password123')
    db_session.add(user)
    db_session.commit()
    
    # Verify user was created
    assert user.id is not None
    assert user.username == 'testuser'
    assert user.email == 'test@example.com'
    assert user.first_name == 'Test'
    assert user.last_name == 'User'
    assert user.role == 'customer'
    assert user.is_active is True
    
    # Verify timestamps were set by triggers
    assert user.created_at is not None
    assert user.updated_at is not None
    assert isinstance(user.created_at, datetime)
    assert isinstance(user.updated_at, datetime)

def test_password_hashing(db_session):
    """Test password hashing and verification"""
    user = User(
        username='passwordtest',
        email='password@test.com',
        first_name='Password',
        last_name='Test',
        role='customer'
    )
    password = 'testpass123'
    user.set_password(password)
    
    # Verify password was hashed
    assert user.password_hash != password
    assert user.check_password(password) is True
    assert user.check_password('wrongpass') is False

def test_unique_constraints(db_session):
    """Test unique constraints on username and email"""
    user1 = User(
        username='unique',
        email='unique@test.com',
        first_name='Unique',
        last_name='Test',
        role='customer'
    )
    user1.set_password('pass123')
    db_session.add(user1)
    db_session.commit()
    
    # Try creating user with same username
    user2 = User(
        username='unique',
        email='different@test.com',
        first_name='Different',
        last_name='User',
        role='customer'
    )
    user2.set_password('pass123')
    db_session.add(user2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()
    
    # Try creating user with same email
    user3 = User(
        username='different',
        email='unique@test.com',
        first_name='Different',
        last_name='User',
        role='customer'
    )
    user3.set_password('pass123')
    db_session.add(user3)
    with pytest.raises(IntegrityError):
        db_session.commit()

def test_role_validation():
    """Test role validation"""
    with pytest.raises(ValueError) as exc_info:
        User(
            username='roletest',
            email='role@test.com',
            first_name='Role',
            last_name='Test',
            role='invalid_role'
        )
    assert 'Invalid role' in str(exc_info.value)

def test_email_validation():
    """Test email validation"""
    with pytest.raises(ValueError) as exc_info:
        User(
            username='emailtest',
            email='invalid_email',
            first_name='Email',
            last_name='Test',
            role='customer'
        )
    assert 'Invalid email address' in str(exc_info.value)

def test_to_dict(db_session):
    """Test the to_dict method"""
    user = User(
        username='dicttest',
        email='dict@test.com',
        first_name='Dict',
        last_name='Test',
        role='customer',
        phone_number='1234567890'
    )
    user.set_password('pass123')
    db_session.add(user)
    db_session.commit()
    
    user_dict = user.to_dict()
    assert user_dict['username'] == 'dicttest'
    assert user_dict['email'] == 'dict@test.com'
    assert user_dict['first_name'] == 'Dict'
    assert user_dict['last_name'] == 'Test'
    assert user_dict['role'] == 'customer'
    assert user_dict['phone_number'] == '1234567890'
    assert 'password_hash' not in user_dict
    assert isinstance(user_dict['created_at'], str)
    assert isinstance(user_dict['updated_at'], str)
