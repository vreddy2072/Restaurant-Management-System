import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from backend.services.order_service import OrderService
from backend.models.schemas.order import OrderCreate, OrderUpdate, OrderStatus
from backend.models.orm.order import Order
from backend.models.orm.user import User
from backend.models.orm.shopping_cart import ShoppingCart
from backend.utils.exceptions import NotFoundException, ValidationError

def test_create_order(db_session):
    """Test creating a new order"""
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

    # Create order
    service = OrderService(db_session)
    order_data = OrderCreate(
        customer_name="John Doe",
        is_group_order=False
    )
    order = service.create_order(user.id, order_data)

    # Verify order
    assert order.id is not None
    assert order.order_number.startswith("ORD-")
    assert 1 <= order.table_number <= 10
    assert order.customer_name == "John Doe"
    assert order.is_group_order is False
    assert order.user_id == user.id
    assert order.status == OrderStatus.INITIALIZED

def test_get_order(db_session):
    """Test getting an order by ID"""
    # Create test user and order
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

    order = Order(
        order_number="ORD-001",
        table_number=5,
        customer_name="Jane Doe",
        user_id=user.id,
        status=OrderStatus.INITIALIZED
    )
    db_session.add(order)
    db_session.commit()

    # Test get order
    service = OrderService(db_session)
    retrieved_order = service.get_order(order.id)
    assert retrieved_order.id == order.id
    assert retrieved_order.order_number == "ORD-001"

    # Test get non-existent order
    with pytest.raises(NotFoundException):
        service.get_order(999)

def test_get_user_orders(db_session):
    """Test getting all orders for a user"""
    # Create test user
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

    # Create multiple orders
    orders = [
        Order(
            order_number=f"ORD-00{i}",
            table_number=5,
            customer_name=f"Customer {i}",
            user_id=user.id,
            status=OrderStatus.INITIALIZED
        )
        for i in range(1, 4)
    ]
    db_session.add_all(orders)
    db_session.commit()

    # Test get user orders
    service = OrderService(db_session)
    user_orders = service.get_user_orders(user.id)
    assert len(user_orders) == 3
    assert all(order.user_id == user.id for order in user_orders)

def test_update_order(db_session):
    """Test updating an order"""
    # Create test user and order
    user = User(
        username="testuser4",
        email="test4@example.com",
        password_hash="hashedpassword",
        first_name="Test",
        last_name="User",
        role="customer"
    )
    db_session.add(user)
    db_session.commit()

    order = Order(
        order_number="ORD-004",
        table_number=5,
        customer_name="Bob Wilson",
        user_id=user.id,
        status=OrderStatus.INITIALIZED
    )
    db_session.add(order)
    db_session.commit()

    # Test update order status
    service = OrderService(db_session)
    update_data = OrderUpdate(status=OrderStatus.IN_PROGRESS)
    updated_order = service.update_order(order.id, update_data)
    assert updated_order.status == OrderStatus.IN_PROGRESS

def test_link_cart_to_order(db_session):
    """Test linking a shopping cart to an order"""
    # Create test user
    user = User(
        username="testuser5",
        email="test5@example.com",
        password_hash="hashedpassword",
        first_name="Test",
        last_name="User",
        role="customer"
    )
    db_session.add(user)
    db_session.commit()

    # Create order and cart
    order = Order(
        order_number="ORD-005",
        table_number=5,
        customer_name="Charlie Brown",
        user_id=user.id,
        status=OrderStatus.INITIALIZED
    )
    cart = ShoppingCart(user_id=user.id)
    db_session.add_all([order, cart])
    db_session.commit()

    # Test linking cart
    service = OrderService(db_session)
    updated_order = service.link_cart_to_order(order.id, cart.id)
    
    # Verify cart is linked via order_number
    assert cart.order_number == order.order_number
    assert updated_order.status == OrderStatus.IN_PROGRESS

    # Test linking invalid cart
    with pytest.raises(ValidationError):
        service.link_cart_to_order(order.id, 999)

    # Test linking cart from different user
    other_user = User(
        username="otheruser",
        email="other@example.com",
        password_hash="hashedpassword",
        first_name="Other",
        last_name="User",
        role="customer"
    )
    db_session.add(other_user)
    db_session.commit()

    other_cart = ShoppingCart(user_id=other_user.id)
    db_session.add(other_cart)
    db_session.commit()

    with pytest.raises(ValidationError):
        service.link_cart_to_order(order.id, other_cart.id)

def test_cancel_order(db_session):
    """Test cancelling an order"""
    # Create test user and order
    user = User(
        username="testuser6",
        email="test6@example.com",
        password_hash="hashedpassword",
        first_name="Test",
        last_name="User",
        role="customer"
    )
    db_session.add(user)
    db_session.commit()

    order = Order(
        order_number="ORD-006",
        table_number=5,
        customer_name="David Miller",
        user_id=user.id,
        status=OrderStatus.INITIALIZED
    )
    db_session.add(order)
    db_session.commit()

    # Test cancel order
    service = OrderService(db_session)
    cancelled_order = service.cancel_order(order.id)
    assert cancelled_order.status == OrderStatus.CANCELLED

    # Test cancelling already cancelled order
    with pytest.raises(ValidationError):
        service.cancel_order(order.id)

def test_confirm_order(db_session):
    """Test confirming an order"""
    # Create test user
    user = User(
        username="testuser7",
        email="test7@example.com",
        password_hash="hashedpassword",
        first_name="Test",
        last_name="User",
        role="customer"
    )
    db_session.add(user)
    db_session.commit()

    # Create order and cart
    order = Order(
        order_number="ORD-007",
        table_number=5,
        customer_name="Eve Wilson",
        user_id=user.id,
        status=OrderStatus.IN_PROGRESS
    )
    db_session.add(order)
    db_session.commit()

    cart = ShoppingCart(user_id=user.id, order_number=order.order_number)
    db_session.add(cart)
    db_session.commit()

    # Test confirm order
    service = OrderService(db_session)
    confirmed_order = service.confirm_order(order.id)
    assert confirmed_order.status == OrderStatus.CONFIRMED

    # Test confirming order without cart
    order_no_cart = Order(
        order_number="ORD-008",
        table_number=5,
        customer_name="Frank Johnson",
        user_id=user.id,
        status=OrderStatus.IN_PROGRESS
    )
    db_session.add(order_no_cart)
    db_session.commit()

    with pytest.raises(ValidationError):
        service.confirm_order(order_no_cart.id)

    # Test confirming order in wrong status
    order_wrong_status = Order(
        order_number="ORD-009",
        table_number=5,
        customer_name="Grace Lee",
        user_id=user.id,
        status=OrderStatus.INITIALIZED
    )
    db_session.add(order_wrong_status)
    db_session.commit()

    with pytest.raises(ValidationError):
        service.confirm_order(order_wrong_status.id) 