from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the absolute path to the backend directory
BACKEND_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Ensure database directory exists
db_path = BACKEND_DIR / "database"
db_path.mkdir(parents=True, exist_ok=True)

# Database file paths
DB_FILE = db_path / "restaurant.db"
TEST_DB_FILE = db_path / "test.db"

# Get database URL from environment variable or use default with absolute path
if os.getenv("TESTING", "0") == "1":
    DATABASE_URL = f"sqlite:///{TEST_DB_FILE}"
    print(f"Using test database at: {TEST_DB_FILE}")
else:
    DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_FILE}")
    print(f"Using database at: {DB_FILE}")

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def init_db():
    """Initialize the database by creating all tables."""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()