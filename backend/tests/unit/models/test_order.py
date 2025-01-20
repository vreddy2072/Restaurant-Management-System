import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from backend.models.orm.order import Order
from backend.models.schemas.order import OrderCreate, OrderUpdate, OrderResponse, OrderStatus
from backend.models.orm.user import User

def test_create_order(db_session):
    """Test creating a new order"""
    # Create a test user first
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

    # Create an order
    order = Order(
        order_number="ORD-001",
        table_number=5,
        customer_name="John Doe",
        is_group_order=False,
        user_id=user.id,
        status="initialized"
    )
    db_session.add(order)
    db_session.commit()

    # Verify the order was created
    assert order.id is not None
    assert order.order_number == "ORD-001"
    assert order.table_number == 5
    assert order.customer_name == "John Doe"
    assert order.is_group_order is False
    assert order.user_id == user.id
    assert order.status == "initialized"
    assert order.created_at is not None
    assert order.updated_at is not None

def test_order_table_number_constraint(db_session):
    """Test table number constraint"""
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

    # Test invalid table number (too low)
    with pytest.raises(ValueError):
        Order(
            order_number="ORD-002",
            table_number=0,  # Invalid
            customer_name="Jane Doe",
            user_id=user.id
        )

    # Test invalid table number (too high)
    with pytest.raises(ValueError):
        Order(
            order_number="ORD-003",
            table_number=11,  # Invalid
            customer_name="Jane Doe",
            user_id=user.id
        )

def test_order_status_constraint(db_session):
    """Test order status constraint"""
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

    # Try to create order with invalid status
    order = Order(
        order_number="ORD-004",
        table_number=5,
        customer_name="Alice Smith",
        user_id=user.id,
        status="invalid_status"  # Invalid status
    )
    db_session.add(order)
    
    # Should raise an integrity error due to check constraint
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

def test_order_user_relationship(db_session):
    """Test order-user relationship"""
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
        order_number="ORD-005",
        table_number=5,
        customer_name="Bob Wilson",
        user_id=user.id,
        status="initialized"
    )
    db_session.add(order)
    db_session.commit()

    # Test relationship from order to user
    assert order.user.id == user.id
    assert order.user.username == "testuser4"

    # Test relationship from user to orders
    assert len(user.orders) == 1
    assert user.orders[0].order_number == "ORD-005"

def test_order_schema_validation():
    """Test Pydantic schema validation"""
    # Test OrderCreate
    order_data = {
        "customer_name": "David Miller",
        "is_group_order": True
    }
    order_create = OrderCreate(**order_data)
    assert order_create.customer_name == "David Miller"
    assert order_create.is_group_order is True

    # Test OrderCreate with invalid data
    with pytest.raises(ValueError):
        OrderCreate(customer_name="", is_group_order=True)  # Empty name

    # Test OrderUpdate
    update_data = {
        "status": OrderStatus.IN_PROGRESS
    }
    order_update = OrderUpdate(**update_data)
    assert order_update.status == OrderStatus.IN_PROGRESS

    # Test OrderResponse
    response_data = {
        "id": 1,
        "order_number": "ORD-007",
        "table_number": 3,
        "customer_name": "Eve Wilson",
        "is_group_order": False,
        "user_id": 1,
        "status": OrderStatus.INITIALIZED,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    order_response = OrderResponse(**response_data)
    assert order_response.order_number == "ORD-007"
    assert order_response.status == OrderStatus.INITIALIZED

def test_order_to_dict(db_session):
    """Test order to_dict method"""
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
        order_number="ORD-008",
        table_number=7,
        customer_name="Frank Johnson",
        user_id=user.id,
        status="initialized"
    )
    db_session.add(order)
    db_session.commit()

    order_dict = order.to_dict()
    assert order_dict["order_number"] == "ORD-008"
    assert order_dict["table_number"] == 7
    assert order_dict["customer_name"] == "Frank Johnson"
    assert order_dict["status"] == "initialized"
    assert "created_at" in order_dict
    assert "updated_at" in order_dict 