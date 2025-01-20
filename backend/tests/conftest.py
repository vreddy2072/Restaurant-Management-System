import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

# Import Base from utils.database
from backend.utils.database import Base, get_db
from backend.api.app import app
from backend.utils.auth import create_access_token

# Import all models to ensure they are registered with Base
from backend.models.orm.user import User
from backend.models.orm.order import Order
from backend.models.orm.shopping_cart import ShoppingCart, CartItem
from backend.models.orm.menu import MenuItem, Category, Allergen
from backend.models.orm.rating import MenuItemRating, RestaurantFeedback

# Create an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def db_session() -> Session:
    """Create a fresh database session for a test."""
    # Debug: Print all tables in metadata before engine creation
    print("\nTables in metadata before engine creation:", Base.metadata.tables.keys())
    
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Debug: Print all tables in metadata before table creation
    print("\nTables in metadata before table creation:", Base.metadata.tables.keys())
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Debug: Print all tables that were created
    inspector = inspect(engine)
    print("\nCreated tables:", inspector.get_table_names())
    
    # Debug: Print User table columns
    if 'users' in inspector.get_table_names():
        print("\nUser table columns:", [col['name'] for col in inspector.get_columns('users')])
    
    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session: Session) -> TestClient:
    """Create a test client with the test database session."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def test_user(db_session: Session) -> User:
    """Create a test user."""
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash="hashedpassword",
        first_name="Test",
        last_name="User",
        role="customer"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture(scope="function")
def test_user_token(test_user: User) -> str:
    """Create a JWT token for the test user."""
    return create_access_token(data={"sub": test_user.email})

@pytest.fixture(scope="function")
def staff_user(db_session: Session) -> User:
    """Create a staff user."""
    user = User(
        username="staffuser",
        email="staff@example.com",
        password_hash="hashedpassword",
        first_name="Staff",
        last_name="User",
        role="staff",
        is_staff=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture(scope="function")
def sample_category(db_session: Session) -> Category:
    """Create a sample category."""
    category = Category(
        name="Main Course",
        description="Main dishes"
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category

@pytest.fixture(scope="function")
def sample_menu_item(db_session: Session, sample_category: Category) -> MenuItem:
    """Create a sample menu item."""
    menu_item = MenuItem(
        name="Test Dish",
        description="A test dish",
        price=10.99,
        category_id=sample_category.id,
        is_available=True,
        spice_level=1,
        is_vegetarian=True,
        is_vegan=False,
        is_gluten_free=False
    )
    db_session.add(menu_item)
    db_session.commit()
    db_session.refresh(menu_item)
    return menu_item

@pytest.fixture(scope="function")
def sample_menu_item_rating(db_session: Session, test_user: User, sample_menu_item: MenuItem) -> MenuItemRating:
    """Create a sample menu item rating."""
    rating = MenuItemRating(
        user_id=test_user.id,
        menu_item_id=sample_menu_item.id,
        rating=4,
        comment="Good dish"
    )
    db_session.add(rating)
    db_session.commit()
    db_session.refresh(rating)
    return rating

@pytest.fixture(scope="function")
def sample_restaurant_feedback(db_session: Session, test_user: User) -> RestaurantFeedback:
    """Create a sample restaurant feedback."""
    feedback = RestaurantFeedback(
        user_id=test_user.id,
        feedback_text="Great experience overall",
        service_rating=5,
        ambiance_rating=4,
        cleanliness_rating=5,
        value_rating=4
    )
    db_session.add(feedback)
    db_session.commit()
    db_session.refresh(feedback)
    return feedback