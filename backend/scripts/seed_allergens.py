import os
import sys
from pathlib import Path

# Force the correct database path BEFORE importing any modules
backend_dir = Path(__file__).resolve().parent.parent
db_path = backend_dir / "database"
db_path.mkdir(parents=True, exist_ok=True)
db_file = db_path / "restaurant.db"

# Override DATABASE_URL in environment
os.environ["DATABASE_URL"] = f"sqlite:///{db_file.absolute()}"

# Now add the parent directory to Python path and import modules
parent_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(parent_dir))

# Only import after setting up the environment
from backend.models.orm.menu import Allergen
from backend.utils.database import SessionLocal, engine, Base

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

def seed_allergens():
    common_allergens = [
        {"name": "Dairy", "description": "Includes milk, cheese, butter, and other dairy products"},
        {"name": "Eggs", "description": "All varieties of eggs"},
        {"name": "Fish", "description": "All species of fish"},
        {"name": "Shellfish", "description": "Includes shrimp, crab, lobster, and other shellfish"},
        {"name": "Tree Nuts", "description": "Includes almonds, walnuts, cashews, and other tree nuts"},
        {"name": "Peanuts", "description": "A legume commonly causing allergic reactions"},
        {"name": "Wheat", "description": "All forms of wheat and wheat derivatives"},
        {"name": "Soy", "description": "Soybeans and soy-based products"},
        {"name": "Sesame", "description": "Seeds and oils from sesame"},
        {"name": "Mustard", "description": "Mustard seeds and prepared mustard"},
        {"name": "Celery", "description": "Including celery stalks, leaves, seeds, and root"},
        {"name": "Lupin", "description": "A legume commonly used in flour"},
        {"name": "Sulfites", "description": "Used as a preservative"},
        {"name": "Gluten", "description": "Found in wheat, barley, rye, and some oats"}
    ]

    db = SessionLocal()
    try:
        # Check if allergens already exist
        existing_allergens = db.query(Allergen).all()
        print(f"Found {len(existing_allergens)} existing allergens in {db_file}")
        
        if len(existing_allergens) > 0:
            print("Existing allergens:", [a.name for a in existing_allergens])
            return

        # Add allergens
        print(f"Adding new allergens to database: {db_file}")
        for allergen_data in common_allergens:
            allergen = Allergen(**allergen_data)
            db.add(allergen)
            print(f"Added allergen: {allergen_data['name']}")
        
        db.commit()
        print("Successfully seeded allergens!")
    
    except Exception as e:
        print(f"Error seeding allergens: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print(f"Using database at: {db_file.absolute()}")
    print(f"Database URL: {os.environ['DATABASE_URL']}")
    seed_allergens()
