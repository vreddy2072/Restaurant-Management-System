import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from backend.models.orm.menu import MenuItem, Category

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
