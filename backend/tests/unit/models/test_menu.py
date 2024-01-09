import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from backend.models.orm.menu import MenuItem, Category, Allergen

def test_create_menu_item(db_session):
    """Test creating a new menu item"""
    # Create a category first
    category = Category(name="Test Category", description="Test category")
    db_session.add(category)
    db_session.commit()

    item = MenuItem(
        name="Test Item",
        description="A test menu item",
        price=9.99,
        category=category,
        image_url="http://example.com/image.jpg"
    )
    db_session.add(item)
    db_session.commit()

    assert item.id is not None
    assert item.name == "Test Item"
    assert item.description == "A test menu item"
    assert item.price == 9.99
    assert item.category.name == "Test Category"
    assert item.image_url == "http://example.com/image.jpg"
    assert item.is_active is True
    assert isinstance(item.created_at, datetime)
    assert isinstance(item.updated_at, datetime)

def test_price_validation():
    """Test price validation"""
    category = Category(name="Test Category 2", description="Test category")
    with pytest.raises(ValueError):
        MenuItem(
            name="Invalid Price",
            description="Item with invalid price",
            price=-10.0,  # Invalid negative price
            category=category
        )

def test_category_validation(db_session):
    """Test category validation"""
    # Test that menu item requires a valid category
    with pytest.raises(IntegrityError):
        item = MenuItem(
            name="No Category",
            description="Item with no category",
            price=9.99,
            category_id=None  # Category is required
        )
        db_session.add(item)
        db_session.commit()
    db_session.rollback()

def test_to_dict(db_session):
    """Test the to_dict method"""
    # Create a category first
    category = Category(name="Test Category 3", description="Test category")
    db_session.add(category)
    db_session.commit()

    item = MenuItem(
        name="Dict Test",
        description="Testing to_dict",
        price=9.99,
        category=category,
        image_url="http://example.com/image.jpg"
    )
    db_session.add(item)
    db_session.commit()

    item_dict = item.to_dict()
    assert item_dict["name"] == "Dict Test"
    assert item_dict["description"] == "Testing to_dict"
    assert item_dict["price"] == 9.99
    assert item_dict["category_id"] == category.id
    assert item_dict["image_url"] == "http://example.com/image.jpg"
    assert item_dict["is_active"] is True

def test_dietary_preferences(db_session):
    """Test dietary preference flags"""
    category = Category(name="Test Category 4", description="Test category")
    db_session.add(category)
    db_session.commit()

    item = MenuItem(
        name="Vegan Dish",
        description="A vegan and gluten-free dish",
        price=12.99,
        category=category,
        is_vegetarian=True,
        is_vegan=True,
        is_gluten_free=True
    )
    db_session.add(item)
    db_session.commit()

    assert item.is_vegetarian is True
    assert item.is_vegan is True
    assert item.is_gluten_free is True

def test_spice_level_validation(db_session):
    """Test spice level validation"""
    category = Category(name="Test Category 5", description="Test category")
    db_session.add(category)
    db_session.commit()

    # Test valid spice level
    item = MenuItem(
        name="Spicy Dish",
        description="A spicy dish",
        price=14.99,
        category=category,
        spice_level=3
    )
    db_session.add(item)
    db_session.commit()
    assert item.spice_level == 3

    # Test invalid spice level
    with pytest.raises(ValueError):
        MenuItem(
            name="Invalid Spice",
            description="Invalid spice level",
            price=14.99,
            category=category,
            spice_level=5  # Invalid: should be 0-3
        )

def test_customization_options(db_session):
    """Test customization options"""
    category = Category(name="Test Category 6", description="Test category")
    db_session.add(category)
    db_session.commit()

    customization = {
        "size": ["small", "medium", "large"],
        "toppings": ["cheese", "mushrooms", "pepperoni"]
    }

    item = MenuItem(
        name="Custom Pizza",
        description="Customizable pizza",
        price=15.99,
        category=category,
        customization_options=customization
    )
    db_session.add(item)
    db_session.commit()

    assert item.customization_options == customization
    assert "size" in item.customization_options
    assert len(item.customization_options["toppings"]) == 3

def test_allergens(db_session):
    """Test allergens relationship"""
    category = Category(name="Test Category 7", description="Test category")
    db_session.add(category)

    allergen1 = Allergen(name="Nuts", description="Contains nuts")
    allergen2 = Allergen(name="Dairy", description="Contains dairy")
    db_session.add_all([allergen1, allergen2])
    db_session.commit()

    item = MenuItem(
        name="Allergen Test",
        description="Testing allergens",
        price=16.99,
        category=category,
        allergens=[allergen1, allergen2]
    )
    db_session.add(item)
    db_session.commit()

    assert len(item.allergens) == 2
    assert allergen1 in item.allergens
    assert allergen2 in item.allergens

def test_rating_functionality(db_session):
    """Test rating functionality"""
    category = Category(name="Test Category 8", description="Test category")
    db_session.add(category)
    db_session.commit()

    item = MenuItem(
        name="Rated Item",
        description="Item with ratings",
        price=18.99,
        category=category,
        average_rating=4.5,
        rating_count=10
    )
    db_session.add(item)
    db_session.commit()

    assert item.average_rating == 4.5
    assert item.rating_count == 10

def test_category_cascade(db_session):
    """Test category relationship and cascade behavior"""
    category = Category(name="Test Category 9", description="Test category")
    db_session.add(category)
    db_session.commit()

    items = [
        MenuItem(name=f"Item {i}", description=f"Description {i}", 
                price=10.99 + i, category=category)
        for i in range(3)
    ]
    db_session.add_all(items)
    db_session.commit()

    # Test that items are associated with category
    assert len(category.menu_items) == 3
    
    # Test cascade behavior when category is deactivated
    category.is_active = False
    db_session.commit()
    
    # Category deactivation should not automatically deactivate items
    assert any(item.is_active for item in category.menu_items)
