import os
os.environ["TESTING"] = "1"  # Set testing environment before any imports

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from pathlib import Path
from backend.utils.database import SessionLocal, init_db, Base, engine, get_db

from backend.api.app import app
from backend.models.orm.menu import Category, MenuItem, Allergen
from backend.models.orm.user import User
from backend.models.orm.shopping_cart import ShoppingCart, CartItem
from backend.models.orm.rating import MenuItemRating, RestaurantFeedback
from backend.utils.auth import create_access_token
from httpx import AsyncClient

# Get the absolute path to the backend directory
BACKEND_DIR = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
BACKEND_DIR = BACKEND_DIR / "backend"

# Ensure test database directory exists
db_path = BACKEND_DIR / "database"
db_path.mkdir(parents=True, exist_ok=True)

# Use a separate test database with absolute path
TEST_DATABASE_URL = f"sqlite:///{db_path}/test.db"

# Create test engine
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}  # Allow SQLite to be used across threads
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="session", autouse=True)
def initialize_database():
    """Initialize the database before running tests"""
    # Drop all tables and recreate them
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

def override_get_db():
    """Override the get_db dependency for testing"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(autouse=True)
def cleanup_database():
    """Clean up database before each test"""
    session = TestingSessionLocal()
    try:
        for table in reversed(Base.metadata.sorted_tables):
            session.execute(table.delete())
        session.commit()
    finally:
        session.close()
    yield

@pytest.fixture
def db_session():
    """Get a database session for each test"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client(db_session):
    """Get a test client"""
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture
async def async_client(db_session):
    """Create an async test client"""
    app.dependency_overrides[get_db] = lambda: db_session
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()

@pytest.fixture
def sample_category(db_session):
    """Create a sample category for testing."""
    from backend.models.orm.menu import Category
    import uuid
    unique_name = f"Test Category {uuid.uuid4()}"
    category = Category(
        name=unique_name,
        description="Test Description"
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category

def get_category(db_session, category_id):
    """Helper function to get a fresh category instance."""
    from backend.models.orm.menu import Category
    return db_session.query(Category).filter(Category.id == category_id).first()

@pytest.fixture
def sample_menu_item(db_session, sample_category):
    """Create a sample menu item for testing."""
    from backend.models.orm.menu import MenuItem
    import uuid
    unique_name = f"Test Item {uuid.uuid4()}"
    menu_item = MenuItem(
        name=unique_name,
        description="Test Item Description",
        price=9.99,
        category_id=sample_category.id,
        is_vegetarian=True,
        spice_level=1,
        preparation_time=15
    )
    db_session.add(menu_item)
    db_session.commit()
    db_session.refresh(menu_item)
    return menu_item

@pytest.fixture
def test_user(db_session):
    """Create a test user for testing."""
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password",
        first_name="Test",
        last_name="User",
        role="customer"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def sample_cart(db_session, test_user):
    """Create a sample shopping cart for testing."""
    cart = ShoppingCart(user_id=test_user.id)
    db_session.add(cart)
    db_session.commit()
    db_session.refresh(cart)
    return cart

@pytest.fixture
def sample_cart_item(db_session, sample_cart, sample_menu_item):
    """Create a sample cart item for testing."""
    cart_item = CartItem(
        cart_id=sample_cart.id,
        menu_item_id=sample_menu_item.id,
        quantity=2,
        customizations={"notes": "Extra spicy"}
    )
    db_session.add(cart_item)
    db_session.commit()
    db_session.refresh(cart_item)
    return cart_item

@pytest.fixture
def sample_menu_item_rating(db_session, test_user, sample_menu_item):
    """Create a sample menu item rating for testing."""
    rating = MenuItemRating(
        user_id=test_user.id,
        menu_item_id=sample_menu_item.id,
        rating=4,
        comment="Great dish!"
    )
    db_session.add(rating)
    db_session.commit()
    db_session.refresh(rating)
    return rating

@pytest.fixture
def sample_restaurant_feedback(db_session, test_user):
    """Create a sample restaurant feedback for testing."""
    feedback = RestaurantFeedback(
        user_id=test_user.id,
        feedback_text="Excellent service and ambiance",
        category="service"
    )
    db_session.add(feedback)
    db_session.commit()
    db_session.refresh(feedback)
    return feedback

@pytest.fixture
def test_menu_item(db_session):
    """Create a test menu item"""
    category = Category(name="Test Category", description="Test Description")
    db_session.add(category)
    db_session.commit()

    menu_item = MenuItem(
        name="Test Item",
        description="Test Description",
        price=9.99,
        category_id=category.id,
        is_active=True,
        image_url="test.jpg"
    )
    db_session.add(menu_item)
    db_session.commit()
    db_session.refresh(menu_item)
    return menu_item

@pytest.fixture
def test_cart(db_session, test_user):
    """Create a test shopping cart"""
    cart = ShoppingCart(user_id=test_user.id)
    db_session.add(cart)
    db_session.commit()
    db_session.refresh(cart)
    return cart

@pytest.fixture
def test_cart_item(db_session, test_cart, test_menu_item):
    """Create a test cart item"""
    cart_item = CartItem(
        cart_id=test_cart.id,
        menu_item_id=test_menu_item.id,
        quantity=1
    )
    db_session.add(cart_item)
    db_session.commit()
    db_session.refresh(cart_item)
    return cart_item

@pytest.fixture
def test_user_token(test_user):
    """Create a JWT token for the test user"""
    return create_access_token(data={"sub": test_user.email})