import pytest
from sqlalchemy.exc import IntegrityError
from backend.services.cart_service import CartService
from backend.models.schemas.cart import CartItemCreate, CartItemUpdate
from backend.models.orm.shopping_cart import ShoppingCart, CartItem
from backend.models.orm.menu import MenuItem
from backend.utils.exceptions import NotFoundException, ValidationError

def test_get_or_create_cart(db_session, test_user):
    """Test getting or creating a cart"""
    service = CartService(db_session)
    
    # Test creating new cart
    cart = service.get_or_create_cart(test_user.id)
    assert cart.user_id == test_user.id
    assert cart.order_number is None
    
    # Test getting existing cart
    same_cart = service.get_or_create_cart(test_user.id)
    assert same_cart.id == cart.id

    # Test getting cart when user has an order-linked cart
    cart.order_number = "ORD-001"
    db_session.commit()

    # Should create new cart since existing one is linked to order
    new_cart = service.get_or_create_cart(test_user.id)
    assert new_cart.id != cart.id
    assert new_cart.order_number is None

def test_get_cart(db_session, test_user):
    """Test getting cart by ID"""
    service = CartService(db_session)
    cart = ShoppingCart(user_id=test_user.id)
    db_session.add(cart)
    db_session.commit()

    retrieved_cart = service.get_cart(cart.id)
    assert retrieved_cart.id == cart.id

    with pytest.raises(NotFoundException):
        service.get_cart(999)

def test_get_user_cart(db_session, test_user):
    """Test getting user's active cart"""
    service = CartService(db_session)
    
    # Create cart linked to order
    ordered_cart = ShoppingCart(user_id=test_user.id, order_number="ORD-001")
    db_session.add(ordered_cart)
    
    # Create active cart
    active_cart = ShoppingCart(user_id=test_user.id)
    db_session.add(active_cart)
    db_session.commit()

    # Should only get active cart
    user_cart = service.get_user_cart(test_user.id)
    assert user_cart.id == active_cart.id
    assert user_cart.order_number is None

def test_get_cart_by_order(db_session, test_user):
    """Test getting cart by order number"""
    service = CartService(db_session)
    
    # Create cart linked to order
    cart = ShoppingCart(user_id=test_user.id, order_number="ORD-001")
    db_session.add(cart)
    db_session.commit()

    # Test getting cart by order number
    retrieved_cart = service.get_cart_by_order("ORD-001")
    assert retrieved_cart.id == cart.id
    assert retrieved_cart.order_number == "ORD-001"

    # Test getting non-existent order
    assert service.get_cart_by_order("ORD-999") is None

def test_add_item_to_cart(db_session, test_user, sample_menu_item):
    """Test adding item to cart"""
    service = CartService(db_session)
    cart = service.get_or_create_cart(test_user.id)
    
    item_data = CartItemCreate(
        menu_item_id=sample_menu_item.id,
        quantity=2,
        customizations={"notes": "Extra spicy"}
    )
    
    cart_item = service.add_item(cart.id, item_data)
    assert cart_item.menu_item_id == sample_menu_item.id
    assert cart_item.quantity == 2
    assert cart_item.customizations == {"notes": "Extra spicy"}

def test_add_item_to_ordered_cart(db_session, test_user, sample_menu_item):
    """Test adding item to cart that's linked to an order"""
    service = CartService(db_session)
    cart = service.get_or_create_cart(test_user.id)
    cart.order_number = "ORD-001"
    db_session.commit()

    item_data = CartItemCreate(
        menu_item_id=sample_menu_item.id,
        quantity=2,
        customizations={"notes": "Extra spicy"}
    )
    
    with pytest.raises(ValidationError, match="Cannot modify cart that is linked to an order"):
        service.add_item(cart.id, item_data)

def test_add_existing_item_to_cart(db_session, test_user, sample_menu_item):
    """Test adding existing item to cart"""
    service = CartService(db_session)
    cart = service.get_or_create_cart(test_user.id)
    
    item_data = CartItemCreate(
        menu_item_id=sample_menu_item.id,
        quantity=2,
        customizations={"notes": "Extra spicy"}
    )
    
    # Add item first time
    cart_item1 = service.add_item(cart.id, item_data)
    
    # Add same item again
    item_data.quantity = 3
    item_data.customizations = {"notes": "Very spicy"}
    cart_item2 = service.add_item(cart.id, item_data)
    
    assert cart_item2.id == cart_item1.id
    assert cart_item2.quantity == 5  # 2 + 3
    assert cart_item2.customizations == {"notes": "Very spicy"}

def test_add_invalid_menu_item(db_session, test_user):
    """Test adding non-existent menu item"""
    service = CartService(db_session)
    cart = service.get_or_create_cart(test_user.id)
    
    item_data = CartItemCreate(
        menu_item_id=999,  # Non-existent menu item
        quantity=1
    )
    
    with pytest.raises(NotFoundException):
        service.add_item(cart.id, item_data)

def test_update_cart_item(db_session, test_user, sample_menu_item):
    """Test updating cart item"""
    service = CartService(db_session)
    cart = service.get_or_create_cart(test_user.id)
    
    # Add item
    item_data = CartItemCreate(
        menu_item_id=sample_menu_item.id,
        quantity=2,
        customizations={"notes": "Extra spicy"}
    )
    cart_item = service.add_item(cart.id, item_data)
    
    # Update item
    update_data = CartItemUpdate(
        quantity=3,
        customizations={"notes": "Less spicy"}
    )
    updated_item = service.update_item(cart.id, cart_item.id, update_data)
    
    assert updated_item.quantity == 3
    assert updated_item.customizations == {"notes": "Less spicy"}

def test_update_item_in_ordered_cart(db_session, test_user, sample_menu_item):
    """Test updating item in cart that's linked to an order"""
    service = CartService(db_session)
    cart = service.get_or_create_cart(test_user.id)
    
    # Add item
    item_data = CartItemCreate(
        menu_item_id=sample_menu_item.id,
        quantity=2
    )
    cart_item = service.add_item(cart.id, item_data)
    
    # Link cart to order
    cart.order_number = "ORD-001"
    db_session.commit()
    
    # Try to update item
    update_data = CartItemUpdate(quantity=3)
    with pytest.raises(ValidationError, match="Cannot modify cart that is linked to an order"):
        service.update_item(cart.id, cart_item.id, update_data)

def test_remove_item_from_cart(db_session, test_user, sample_menu_item):
    """Test removing item from cart"""
    service = CartService(db_session)
    cart = service.get_or_create_cart(test_user.id)
    
    # Add item
    item_data = CartItemCreate(
        menu_item_id=sample_menu_item.id,
        quantity=2
    )
    cart_item = service.add_item(cart.id, item_data)
    
    # Remove item
    service.remove_item(cart.id, cart_item.id)
    
    # Verify item is removed
    cart = service.get_cart(cart.id)
    assert len(cart.cart_items) == 0

def test_remove_item_from_ordered_cart(db_session, test_user, sample_menu_item):
    """Test removing item from cart that's linked to an order"""
    service = CartService(db_session)
    cart = service.get_or_create_cart(test_user.id)
    
    # Add item
    item_data = CartItemCreate(
        menu_item_id=sample_menu_item.id,
        quantity=2
    )
    cart_item = service.add_item(cart.id, item_data)
    
    # Link cart to order
    cart.order_number = "ORD-001"
    db_session.commit()
    
    # Try to remove item
    with pytest.raises(ValidationError, match="Cannot modify cart that is linked to an order"):
        service.remove_item(cart.id, cart_item.id)

def test_clear_cart(db_session, test_user, sample_menu_item):
    """Test clearing all items from cart"""
    service = CartService(db_session)
    cart = service.get_or_create_cart(test_user.id)
    
    # Add items
    item_data1 = CartItemCreate(
        menu_item_id=sample_menu_item.id,
        quantity=2
    )
    item_data2 = CartItemCreate(
        menu_item_id=sample_menu_item.id,
        quantity=1
    )
    service.add_item(cart.id, item_data1)
    service.add_item(cart.id, item_data2)
    
    # Clear cart
    service.clear_cart(cart.id)
    
    # Verify cart is empty
    cart = service.get_cart(cart.id)
    assert len(cart.cart_items) == 0

def test_clear_ordered_cart(db_session, test_user, sample_menu_item):
    """Test clearing cart that's linked to an order"""
    service = CartService(db_session)
    cart = service.get_or_create_cart(test_user.id)
    
    # Add items
    item_data = CartItemCreate(
        menu_item_id=sample_menu_item.id,
        quantity=2
    )
    service.add_item(cart.id, item_data)
    
    # Link cart to order
    cart.order_number = "ORD-001"
    db_session.commit()
    
    # Try to clear cart
    with pytest.raises(ValidationError, match="Cannot modify cart that is linked to an order"):
        service.clear_cart(cart.id)

def test_calculate_cart_total(db_session, test_user, sample_menu_item):
    """Test calculating cart total"""
    service = CartService(db_session)
    cart = service.get_or_create_cart(test_user.id)
    
    # Add items
    item_data = CartItemCreate(
        menu_item_id=sample_menu_item.id,
        quantity=2
    )
    service.add_item(cart.id, item_data)
    
    # Calculate total
    total = service.calculate_cart_total(cart.id)
    assert total == sample_menu_item.price * 2
