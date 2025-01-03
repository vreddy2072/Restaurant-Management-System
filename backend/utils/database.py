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

# Get database URL from environment variable or use default with absolute path
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{db_path}/restaurant.db")

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Only needed for SQLite
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

def init_db():
    """Initialize the database by creating tables only if they don't exist."""
    inspector = inspect(engine)
    tables_before = inspector.get_table_names()
    print(f"Tables before initialization: {tables_before}")
    
    # Import models to register them with Base
    from backend.models.orm.menu import Category, MenuItem  # noqa: F401
    
    # Only create tables if they don't exist
    if not tables_before:
        print("Initializing database tables...")
        Base.metadata.create_all(bind=engine)
        
        # Verify tables were created
        inspector = inspect(engine)
        tables_after = inspector.get_table_names()
        print(f"Tables after initialization: {tables_after}")
        
        # Show table details
        for table_name in tables_after:
            columns = inspector.get_columns(table_name)
            print(f"\nTable '{table_name}' columns:")
            for column in columns:
                print(f"  - {column['name']}: {column['type']}")
    else:
        print(f"Database tables already exist: {tables_before}")
        # Show existing table details
        for table_name in tables_before:
            columns = inspector.get_columns(table_name)
            print(f"\nTable '{table_name}' columns:")
            for column in columns:
                print(f"  - {column['name']}: {column['type']}")

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 