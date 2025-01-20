import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.models.orm.user import User
from backend.models.orm.order import Order
from backend.models.orm.shopping_cart import ShoppingCart
from backend.models.schemas.order import OrderStatus

def test_create_order(client: TestClient, db_session: Session, test_user: User):
    """Test creating a new order"""
    response = client.post(
        "/api/orders",
        json={
            "customer_name": "John Doe",
            "is_group_order": False
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["customer_name"] == "John Doe"
    assert data["is_group_order"] is False
    assert data["status"] == OrderStatus.INITIALIZED
    assert data["user_id"] == test_user.id
    assert 1 <= data["table_number"] <= 10

def test_get_order(client: TestClient, db_session: Session, test_user: User):
    """Test getting an order by ID"""
    # Create test order
    order = Order(
        order_number="TEST-001",
        table_number=5,
        customer_name="Jane Doe",
        user_id=test_user.id,
        status=OrderStatus.INITIALIZED
    )
    db_session.add(order)
    db_session.commit()

    # Test get order
    response = client.get(f"/api/orders/{order.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["order_number"] == "TEST-001"
    assert data["customer_name"] == "Jane Doe"

def test_get_user_orders(client: TestClient, db_session: Session, test_user: User):
    """Test getting all orders for a user"""
    # Create multiple test orders
    orders = [
        Order(
            order_number=f"TEST-00{i}",
            table_number=5,
            customer_name=f"Customer {i}",
            user_id=test_user.id,
            status=OrderStatus.INITIALIZED
        )
        for i in range(1, 4)
    ]
    db_session.add_all(orders)
    db_session.commit()

    # Test get user orders
    response = client.get("/api/orders")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert all(order["user_id"] == test_user.id for order in data)

def test_update_order(client: TestClient, db_session: Session, test_user: User):
    """Test updating an order"""
    # Create test order
    order = Order(
        order_number="TEST-004",
        table_number=5,
        customer_name="Bob Wilson",
        user_id=test_user.id,
        status=OrderStatus.INITIALIZED
    )
    db_session.add(order)
    db_session.commit()

    # Test update order
    response = client.put(
        f"/api/orders/{order.id}",
        json={"status": OrderStatus.IN_PROGRESS}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == OrderStatus.IN_PROGRESS

def test_link_cart_to_order(client: TestClient, db_session: Session, test_user: User):
    """Test linking a shopping cart to an order"""
    # Create test order and cart
    order = Order(
        order_number="TEST-005",
        table_number=5,
        customer_name="Charlie Brown",
        user_id=test_user.id,
        status=OrderStatus.INITIALIZED
    )
    cart = ShoppingCart(user_id=test_user.id)
    db_session.add_all([order, cart])
    db_session.commit()

    # Test link cart
    response = client.post(f"/api/orders/{order.id}/link-cart/{cart.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["cart_id"] == cart.id
    assert data["status"] == OrderStatus.IN_PROGRESS

def test_cancel_order(client: TestClient, db_session: Session, test_user: User):
    """Test cancelling an order"""
    # Create test order
    order = Order(
        order_number="TEST-006",
        table_number=5,
        customer_name="David Miller",
        user_id=test_user.id,
        status=OrderStatus.INITIALIZED
    )
    db_session.add(order)
    db_session.commit()

    # Test cancel order
    response = client.post(f"/api/orders/{order.id}/cancel")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == OrderStatus.CANCELLED

def test_confirm_order(client: TestClient, db_session: Session, test_user: User):
    """Test confirming an order"""
    # Create test order and cart
    cart = ShoppingCart(user_id=test_user.id)
    db_session.add(cart)
    db_session.commit()

    order = Order(
        order_number="TEST-007",
        table_number=5,
        customer_name="Eve Wilson",
        user_id=test_user.id,
        status=OrderStatus.IN_PROGRESS,
        cart_id=cart.id
    )
    db_session.add(order)
    db_session.commit()

    # Test confirm order
    response = client.post(f"/api/orders/{order.id}/confirm")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == OrderStatus.CONFIRMED

def test_get_orders_by_status(client: TestClient, db_session: Session, test_user: User, staff_user: User):
    """Test getting orders by status (staff only)"""
    # Create test orders with different statuses
    orders = [
        Order(
            order_number=f"TEST-00{i}",
            table_number=5,
            customer_name=f"Customer {i}",
            user_id=test_user.id,
            status=OrderStatus.IN_PROGRESS
        )
        for i in range(1, 4)
    ]
    db_session.add_all(orders)
    db_session.commit()

    # Test get orders by status (as staff)
    client.headers["Authorization"] = f"Bearer {staff_user.get_token()}"
    response = client.get(f"/api/orders/status/{OrderStatus.IN_PROGRESS}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert all(order["status"] == OrderStatus.IN_PROGRESS for order in data)

    # Test get orders by status (as regular user)
    client.headers["Authorization"] = f"Bearer {test_user.get_token()}"
    response = client.get(f"/api/orders/status/{OrderStatus.IN_PROGRESS}")
    assert response.status_code == 403 