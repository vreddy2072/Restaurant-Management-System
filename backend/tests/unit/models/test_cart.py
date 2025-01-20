import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from backend.models.orm.shopping_cart import ShoppingCart, CartItem
from backend.models.orm.user import User
from backend.models.orm.menu import MenuItem, Category
from backend.models.schemas.cart import (
    CartItemCreate, CartItemUpdate, CartItem as CartItemSchema,
    ShoppingCartCreate, ShoppingCartUpdate, CartResponse
)

def test_create_shopping_cart(db_session):
    """Test creating a new shopping cart"""
    # Create test user
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

    # Create shopping cart
    cart = ShoppingCart(
        user_id=user.id,
        order_number=None
    )
    db_session.add(cart)
    db_session.commit()

    # Verify cart was created
    assert cart.id is not None
    assert cart.user_id == user.id
    assert cart.order_number is None
    assert cart.created_at is not None
    assert cart.updated_at is not None

def test_cart_schema_validation():
    """Test Pydantic schema validation"""
    # Test ShoppingCartCreate
    cart_data = {
        "user_id": 1,
        "order_number": None
    }
    cart_create = ShoppingCartCreate(**cart_data)
    assert cart_create.user_id == 1
    assert cart_create.order_number is None

    # Test ShoppingCartUpdate
    update_data = {
        "order_number": "ORD-001"
    }
    cart_update = ShoppingCartUpdate(**update_data)
    assert cart_update.order_number == "ORD-001"

    # Test CartResponse
    response_data = {
        "id": 1,
        "user_id": 1,
        "order_number": "ORD-001",
        "items": [],
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    cart_response = CartResponse(**response_data)
    assert cart_response.order_number == "ORD-001"
    assert cart_response.items == []

def test_cart_user_relationship(db_session):
    """Test cart-user relationship"""
    # Create test user
    user = User(
        username="testuser2",
        email="test2@example.com",
        password_hash="hashedpassword",
        first_name="Test",
        last_name="User",
        role="customer"
    )
    db_session.add(user)
    db_session.commit()

    # Create shopping cart
    cart = ShoppingCart(user_id=user.id)
    db_session.add(cart)
    db_session.commit()

    # Test relationships
    assert cart.user.id == user.id
    assert len(user.shopping_carts) == 1
    assert user.shopping_carts[0].id == cart.id

def test_cart_items(db_session):
    """Test cart items functionality"""
    # Create test user and cart
    user = User(
        username="testuser3",
        email="test3@example.com",
        password_hash="hashedpassword",
        first_name="Test",
        last_name="User",
        role="customer"
    )
    db_session.add(user)
    db_session.commit()

    cart = ShoppingCart(user_id=user.id)
    db_session.add(cart)
    db_session.commit()

    # Create test category and menu item
    category = Category(name="Test Category")
    db_session.add(category)
    db_session.commit()

    menu_item = MenuItem(
        name="Test Item",
        price=9.99,
        category_id=category.id
    )
    db_session.add(menu_item)
    db_session.commit()

    # Create cart item
    cart_item = CartItem(
        cart_id=cart.id,
        menu_item_id=menu_item.id,
        quantity=2,
        customizations={"notes": "Extra spicy"}
    )
    db_session.add(cart_item)
    db_session.commit()

    # Test relationships and data
    assert len(cart.cart_items) == 1
    assert cart.cart_items[0].quantity == 2
    assert cart.cart_items[0].menu_item.name == "Test Item"
    assert cart.cart_items[0].customizations == {"notes": "Extra spicy"}
