import pytest
from sqlalchemy.orm import Session
from fastapi import HTTPException
from backend.services.menu_service import MenuService
from backend.models.schemas.menu import (
    CategoryCreate, CategoryUpdate,
    MenuItemCreate, MenuItemUpdate,
    AllergenCreate, AllergenUpdate,
    MenuItemFilters
)

def test_create_category(db_session: Session):
    """Test creating a new category"""
    category_data = CategoryCreate(name="Test Category", description="Test Description")
    category = MenuService.create_category(db_session, category_data)
    
    assert category.name == "Test Category"
    assert category.description == "Test Description"
    assert category.is_active is True

def test_create_duplicate_category(db_session: Session):
    """Test creating a category with duplicate name"""
    category_data = CategoryCreate(name="Duplicate Category")
    MenuService.create_category(db_session, category_data)
    
    with pytest.raises(HTTPException) as exc_info:
        MenuService.create_category(db_session, category_data)
    assert exc_info.value.status_code == 400
    assert "already exists" in str(exc_info.value.detail)

def test_get_category(db_session: Session):
    """Test retrieving a category"""
    category_data = CategoryCreate(name="Get Category")
    created_category = MenuService.create_category(db_session, category_data)
    
    retrieved_category = MenuService.get_category(db_session, created_category.id)
    assert retrieved_category.name == "Get Category"

def test_get_nonexistent_category(db_session: Session):
    """Test retrieving a non-existent category"""
    with pytest.raises(HTTPException) as exc_info:
        MenuService.get_category(db_session, 999)
    assert exc_info.value.status_code == 404

def test_get_categories(db_session: Session):
    """Test retrieving all categories"""
    # Create multiple categories
    categories = [
        CategoryCreate(name=f"Category {i}")
        for i in range(3)
    ]
    for category in categories:
        MenuService.create_category(db_session, category)
    
    retrieved_categories = MenuService.get_categories(db_session)
    assert len(retrieved_categories) >= 3

def test_get_active_categories(db_session: Session):
    """Test retrieving only active categories"""
    # Create active and inactive categories
    active_category = MenuService.create_category(
        db_session, CategoryCreate(name="Active Category")
    )
    inactive_category = MenuService.create_category(
        db_session, CategoryCreate(name="Inactive Category")
    )
    MenuService.update_category(
        db_session,
        inactive_category.id,
        CategoryUpdate(is_active=False)
    )
    
    categories = MenuService.get_categories(db_session, active_only=True)
    category_names = [c.name for c in categories]
    assert "Active Category" in category_names
    assert "Inactive Category" not in category_names

def test_update_category(db_session: Session):
    """Test updating a category"""
    category = MenuService.create_category(
        db_session, CategoryCreate(name="Original Name")
    )
    
    updated = MenuService.update_category(
        db_session,
        category.id,
        CategoryUpdate(name="Updated Name", description="Updated Description")
    )
    
    assert updated.name == "Updated Name"
    assert updated.description == "Updated Description"

def test_delete_category(db_session: Session):
    """Test soft deleting a category"""
    category = MenuService.create_category(
        db_session, CategoryCreate(name="To Delete")
    )
    
    MenuService.delete_category(db_session, category.id)
    
    # Category should still exist but be inactive
    deleted_category = MenuService.get_category(db_session, category.id)
    assert deleted_category.is_active is False

def test_create_menu_item(db_session: Session):
    """Test creating a new menu item"""
    # Create a category first
    category = MenuService.create_category(
        db_session, CategoryCreate(name="Food Category")
    )
    
    menu_item_data = MenuItemCreate(
        name="Test Item",
        description="Test Description",
        price=9.99,
        category_id=category.id,
        is_vegetarian=True,
        spice_level=2
    )
    
    menu_item = MenuService.create_menu_item(db_session, menu_item_data)
    
    assert menu_item.name == "Test Item"
    assert menu_item.price == 9.99
    assert menu_item.is_vegetarian is True
    assert menu_item.spice_level == 2

def test_create_menu_item_with_allergens(db_session: Session):
    """Test creating a menu item with allergens"""
    category = MenuService.create_category(
        db_session, CategoryCreate(name="Allergen Test Category")
    )
    
    # Create allergens
    allergen1 = MenuService.create_allergen(
        db_session, AllergenCreate(name="Nuts", description="Contains nuts")
    )
    allergen2 = MenuService.create_allergen(
        db_session, AllergenCreate(name="Dairy", description="Contains dairy")
    )
    
    menu_item_data = MenuItemCreate(
        name="Allergenic Item",
        price=12.99,
        category_id=category.id,
        allergen_ids=[allergen1.id, allergen2.id]
    )
    
    menu_item = MenuService.create_menu_item(db_session, menu_item_data)
    
    assert len(menu_item.allergens) == 2
    allergen_names = {a.name for a in menu_item.allergens}
    assert allergen_names == {"Nuts", "Dairy"}

def test_get_menu_items(db_session: Session):
    """Test retrieving menu items"""
    category = MenuService.create_category(
        db_session, CategoryCreate(name="Items Category")
    )
    
    # Create multiple menu items
    items = [
        MenuItemCreate(
            name=f"Item {i}",
            price=10.0 + i,
            category_id=category.id
        )
        for i in range(3)
    ]
    
    for item in items:
        MenuService.create_menu_item(db_session, item)
    
    retrieved_items = MenuService.get_menu_items(db_session)
    assert len(retrieved_items) >= 3

def test_get_menu_items_by_category(db_session: Session):
    """Test retrieving menu items filtered by category"""
    category1 = MenuService.create_category(
        db_session, CategoryCreate(name="Category 1")
    )
    category2 = MenuService.create_category(
        db_session, CategoryCreate(name="Category 2")
    )
    
    # Create items in different categories
    MenuService.create_menu_item(
        db_session,
        MenuItemCreate(name="Item 1", price=10.0, category_id=category1.id)
    )
    MenuService.create_menu_item(
        db_session,
        MenuItemCreate(name="Item 2", price=12.0, category_id=category2.id)
    )
    
    items_cat1 = MenuService.get_menu_items(db_session, category_id=category1.id)
    assert len(items_cat1) == 1
    assert items_cat1[0].name == "Item 1"

def test_update_menu_item(db_session: Session):
    """Test updating a menu item"""
    category = MenuService.create_category(
        db_session, CategoryCreate(name="Update Test Category")
    )
    
    item = MenuService.create_menu_item(
        db_session,
        MenuItemCreate(name="Original Item", price=10.0, category_id=category.id)
    )
    
    updated = MenuService.update_menu_item(
        db_session,
        item.id,
        MenuItemUpdate(
            name="Updated Item",
            price=15.0,
            is_vegetarian=True
        )
    )
    
    assert updated.name == "Updated Item"
    assert updated.price == 15.0
    assert updated.is_vegetarian is True

def test_delete_menu_item(db_session: Session):
    """Test soft deleting a menu item"""
    category = MenuService.create_category(
        db_session, CategoryCreate(name="Delete Test Category")
    )
    
    item = MenuService.create_menu_item(
        db_session,
        MenuItemCreate(name="To Delete", price=10.0, category_id=category.id)
    )
    
    MenuService.delete_menu_item(db_session, item.id)
    
    # Item should still exist but be inactive
    deleted_item = MenuService.get_menu_item(db_session, item.id)
    assert deleted_item.is_active is False

def test_get_full_menu(db_session: Session):
    """Test retrieving the full menu with categories and items"""
    # Create categories
    category1 = MenuService.create_category(
        db_session, CategoryCreate(name="Full Menu Category 1")
    )
    category2 = MenuService.create_category(
        db_session, CategoryCreate(name="Full Menu Category 2")
    )
    
    # Create items in each category
    for category in [category1, category2]:
        for i in range(2):
            MenuService.create_menu_item(
                db_session,
                MenuItemCreate(
                    name=f"Item {i} in {category.name}",
                    price=10.0 + i,
                    category_id=category.id
                )
            )
    
    full_menu = MenuService.get_full_menu(db_session)
    
    assert len(full_menu) >= 2
    for category in full_menu:
        assert len(category.menu_items) >= 2

def test_filter_menu_items(db_session: Session):
    """Test filtering menu items with various criteria"""
    # Create a category
    category = MenuService.create_category(
        db_session, CategoryCreate(name="Filter Test Category")
    )
    
    # Create allergens
    allergen1 = MenuService.create_allergen(
        db_session, AllergenCreate(name="Nuts", description="Contains nuts")
    )
    allergen2 = MenuService.create_allergen(
        db_session, AllergenCreate(name="Dairy", description="Contains dairy")
    )
    
    # Create menu items with different properties
    items = [
        MenuItemCreate(
            name="Vegetarian Item",
            description="A vegetarian dish",
            price=12.99,
            category_id=category.id,
            is_vegetarian=True,
            is_vegan=False,
            is_gluten_free=True,
            allergen_ids=[allergen1.id]
        ),
        MenuItemCreate(
            name="Vegan Item",
            description="A vegan dish",
            price=14.99,
            category_id=category.id,
            is_vegetarian=True,
            is_vegan=True,
            is_gluten_free=True
        ),
        MenuItemCreate(
            name="Regular Item",
            description="A regular dish",
            price=16.99,
            category_id=category.id,
            is_vegetarian=False,
            is_vegan=False,
            is_gluten_free=False,
            allergen_ids=[allergen1.id, allergen2.id]
        )
    ]
    
    for item in items:
        MenuService.create_menu_item(db_session, item)
    
    # Test vegetarian filter
    vegetarian_items = MenuService.filter_menu_items(
        db_session,
        is_vegetarian=True
    )
    assert len(vegetarian_items) == 2
    assert all(item.is_vegetarian for item in vegetarian_items)
    
    # Test vegan filter
    vegan_items = MenuService.filter_menu_items(
        db_session,
        is_vegan=True
    )
    assert len(vegan_items) == 1
    assert all(item.is_vegan for item in vegan_items)
    
    # Test gluten-free filter
    gluten_free_items = MenuService.filter_menu_items(
        db_session,
        is_gluten_free=True
    )
    assert len(gluten_free_items) == 2
    assert all(item.is_gluten_free for item in gluten_free_items)
    
    # Test price range filter
    price_range_items = MenuService.filter_menu_items(
        db_session,
        min_price=13.00,
        max_price=15.00
    )
    assert len(price_range_items) == 1
    assert all(13.00 <= item.price <= 15.00 for item in price_range_items)
    
    # Test allergen exclusion
    allergen_excluded_items = MenuService.filter_menu_items(
        db_session,
        allergen_exclude_ids=[allergen1.id]
    )
    assert len(allergen_excluded_items) == 1
    for item in allergen_excluded_items:
        assert allergen1.id not in [a.id for a in item.allergens]

def test_get_filtered_menu_items(db_session: Session):
    """Test filtering menu items using MenuItemFilters"""
    # Create a category
    category = MenuService.create_category(
        db_session, CategoryCreate(name="Advanced Filter Category")
    )
    
    # Create menu items with different properties
    items = [
        MenuItemCreate(
            name="Premium Item",
            description="An expensive item",
            price=25.99,
            category_id=category.id,
            is_vegetarian=True
        ),
        MenuItemCreate(
            name="Budget Item",
            description="An affordable item",
            price=9.99,
            category_id=category.id,
            is_vegetarian=False
        ),
        MenuItemCreate(
            name="Mid-range Item",
            description="A moderately priced item",
            price=15.99,
            category_id=category.id,
            is_vegetarian=True
        )
    ]
    
    created_items = []
    for item in items:
        created_item = MenuService.create_menu_item(db_session, item)
        created_items.append(created_item)
    
    # Set ratings by updating the menu items in the database
    from backend.models.orm.menu import MenuItem
    db_session.query(MenuItem).filter(MenuItem.id == created_items[0].id).update({
        "average_rating": 4.5,
        "rating_count": 10
    })
    db_session.query(MenuItem).filter(MenuItem.id == created_items[1].id).update({
        "average_rating": 3.5,
        "rating_count": 8
    })
    db_session.query(MenuItem).filter(MenuItem.id == created_items[2].id).update({
        "average_rating": 4.0,
        "rating_count": 12
    })
    db_session.commit()
    
    # Create filters
    filters = MenuItemFilters(
        category_id=category.id,
        is_vegetarian=True,
        min_price=10.00,
        max_price=20.00,
        min_rating=4.0
    )
    
    # Test filtered items
    filtered_items = MenuService.get_filtered_menu_items(db_session, filters)
    assert len(filtered_items) == 1
    assert filtered_items[0].name == "Mid-range Item"
    assert filtered_items[0].is_vegetarian
    assert 10.00 <= filtered_items[0].price <= 20.00
    assert filtered_items[0].average_rating >= 4.0

def test_delete_allergen(db_session: Session):
    """Test deleting an allergen"""
    # Create an allergen
    allergen = MenuService.create_allergen(
        db_session,
        AllergenCreate(name="Test Allergen", description="Test Description")
    )
    
    # Delete the allergen
    result = MenuService.delete_allergen(db_session, allergen.id)
    assert result is True
    
    # Verify allergen is deleted
    with pytest.raises(HTTPException) as exc_info:
        MenuService.get_allergen(db_session, allergen.id)
    assert exc_info.value.status_code == 404

def test_delete_nonexistent_allergen(db_session: Session):
    """Test deleting a non-existent allergen"""
    with pytest.raises(HTTPException) as exc_info:
        MenuService.delete_allergen(db_session, 999)
    assert exc_info.value.status_code == 404

def test_allergen_operations(db_session: Session):
    """Test CRUD operations for allergens"""
    # Create
    allergen_data = AllergenCreate(name="Test Allergen", description="Test Description")
    allergen = MenuService.create_allergen(db_session, allergen_data)
    assert allergen.name == "Test Allergen"
    
    # Read
    retrieved = MenuService.get_allergen(db_session, allergen.id)
    assert retrieved.name == "Test Allergen"
    
    # Update
    updated = MenuService.update_allergen(
        db_session,
        allergen.id,
        AllergenUpdate(description="Updated Description")
    )
    assert updated.description == "Updated Description"
    
    # Delete
    success = MenuService.delete_allergen(db_session, allergen.id)
    assert success is True
    
    # Verify deletion
    with pytest.raises(HTTPException):
        MenuService.get_allergen(db_session, allergen.id) 