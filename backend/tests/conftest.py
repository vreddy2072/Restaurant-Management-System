import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from pathlib import Path
import os
from alembic import command
from alembic.config import Config

from backend.api.app import app
from backend.utils.database import Base
from backend.utils.database import get_db

# Get the absolute path to the backend directory
BACKEND_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Ensure test database directory exists
db_path = BACKEND_DIR / "database"
db_path.mkdir(parents=True, exist_ok=True)

# Use a separate test database with absolute path
TEST_DATABASE_URL = f"sqlite:///{db_path}/test.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    # Create test database tables using Alembic migrations
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", TEST_DATABASE_URL)
    command.upgrade(alembic_cfg, "head")
    
    # Create a new session for the test
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Drop all tables after the test
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
            
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    del app.dependency_overrides[get_db]

@pytest.fixture
def sample_category(db_session):
    """Create a sample category for testing."""
    from backend.models.orm.menu import Category
    category = Category(
        name="Test Category",
        description="Test Description"
    )
    db_session.add(category)
    db_session.commit()
    return category.id

def get_category(db_session, category_id):
    """Helper function to get a fresh category instance."""
    from backend.models.orm.menu import Category
    return db_session.query(Category).filter(Category.id == category_id).first()

@pytest.fixture
def sample_menu_item(db_session, sample_category):
    """Create a sample menu item for testing."""
    from backend.models.orm.menu import MenuItem
    menu_item = MenuItem(
        name="Test Item",
        description="Test Item Description",
        price=9.99,
        category_id=sample_category,
        is_vegetarian=True,
        spice_level=1,
        preparation_time=15
    )
    db_session.add(menu_item)
    db_session.commit()
    db_session.refresh(menu_item)
    return menu_item