import pytest
from fastapi import HTTPException
from backend.services.menu import MenuService
from backend.models.schemas.menu import CategoryCreate, CategoryUpdate, MenuItemCreate, MenuItemUpdate
from backend.models.orm.menu import Category

def test_create_category(db_session):
    category_data = CategoryCreate(name="Test Category", description="Test Description")
    category = MenuService.create_category(db_session, category_data)
    
    assert category.name == "Test Category"
    assert category.description == "Test Description"
    assert category.is_active == True

def test_create_duplicate_category(db_session, sample_category):
    # Get the category name from the database
    from backend.models.orm.menu import Category
    category = db_session.query(Category).filter(Category.id == sample_category).first()
    category_data = CategoryCreate(name=category.name)
    
    with pytest.raises(HTTPException) as exc_info:
        MenuService.create_category(db_session, category_data)
    assert exc_info.value.status_code == 400

def test_get_category(db_session, sample_category):
    category = MenuService.get_category(db_session, sample_category)
    assert category.id == sample_category
    # Get the original category to compare
    from backend.models.orm.menu import Category
    original = db_session.query(Category).filter(Category.id == sample_category).first()
    assert category.name == original.name

def test_get_nonexistent_category(db_session):
    with pytest.raises(HTTPException) as exc_info:
        MenuService.get_category(db_session, 999)
    assert exc_info.value.status_code == 404

def test_update_category(db_session, sample_category):
    update_data = CategoryUpdate(name="Updated Category")
    updated_category = MenuService.update_category(db_session, sample_category, update_data)
    
    assert updated_category.name == "Updated Category"

def test_delete_category(db_session, sample_category):
    MenuService.delete_category(db_session, sample_category)
    category = db_session.query(Category).filter_by(id=sample_category).first()
    assert category.is_active == False

def test_create_menu_item(db_session, sample_category):
    item_data = MenuItemCreate(
        name="Test Item",
        description="Test Description",
        price=9.99,
        category_id=sample_category,
        is_vegetarian=True,
        spice_level=1,
        preparation_time=15
    )
    menu_item = MenuService.create_menu_item(db_session, item_data)
    
    assert menu_item.name == "Test Item"
    assert menu_item.price == 9.99
    assert menu_item.category_id == sample_category

def test_create_menu_item_invalid_category(db_session):
    item_data = MenuItemCreate(
        name="Test Item",
        price=9.99,
        category_id=999
    )
    
    with pytest.raises(HTTPException) as exc_info:
        MenuService.create_menu_item(db_session, item_data)
    assert exc_info.value.status_code == 404

def test_get_menu_item(db_session, sample_menu_item):
    menu_item = MenuService.get_menu_item(db_session, sample_menu_item.id)
    assert menu_item.id == sample_menu_item.id
    assert menu_item.name == sample_menu_item.name

def test_update_menu_item(db_session, sample_menu_item):
    update_data = MenuItemUpdate(
        name="Updated Item",
        price=14.99,
        category_id=sample_menu_item.category_id
    )
    updated_item = MenuService.update_menu_item(db_session, sample_menu_item.id, update_data)
    
    assert updated_item.name == "Updated Item"
    assert updated_item.price == 14.99

def test_delete_menu_item(db_session, sample_menu_item):
    MenuService.delete_menu_item(db_session, sample_menu_item.id)
    menu_item = db_session.query(sample_menu_item.__class__).filter_by(id=sample_menu_item.id).first()
    assert menu_item.is_active == False

def test_get_full_menu(db_session, sample_category, sample_menu_item):
    menu = MenuService.get_full_menu(db_session)
    assert len(menu) > 0
    assert menu[0].menu_items[0].id == sample_menu_item.id 