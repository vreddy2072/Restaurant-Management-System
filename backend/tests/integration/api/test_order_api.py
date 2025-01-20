import pytest
from httpx import Client
from sqlalchemy.orm import Session
import logging

from backend.models.orm.user import User
from backend.models.orm.order import Order
from backend.services.user_service import UserService
from backend.utils.auth import create_access_token

pytestmark = pytest.mark.usefixtures("db_session")

def test_create_order_unauthorized(client: Client):
    """Test that unauthorized users cannot create orders"""
    response = client.post("/api/orders", json={
        "customer_name": "Test Customer",
        "is_group_order": False
    })
    assert response.status_code == 401
    assert "detail" in response.json()
    assert response.json()["detail"] == "Not authenticated"

def test_create_order(client: Client, db_session: Session, test_user: User):
    """Test creating a new order"""
    # Login as test user
    token = create_access_token(data={"sub": test_user.email})
    headers = {"Authorization": f"Bearer {token}"}

    # Create order
    order_data = {
        "customer_name": "Test Customer",
        "is_group_order": False
    }
    response = client.post("/api/orders", json=order_data, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["user_id"] == test_user.id
    assert data["customer_name"] == order_data["customer_name"]
    assert data["is_group_order"] == order_data["is_group_order"]
    assert "order_number" in data
    assert "table_number" in data
    assert data["status"] == "initialized"

def test_get_order(client: Client, db_session: Session, test_user: User):
    """Test getting an order by ID"""
    # Login as test user
    token = create_access_token(data={"sub": test_user.email})
    headers = {"Authorization": f"Bearer {token}"}

    # Create order first
    order_data = {
        "customer_name": "Test Customer",
        "is_group_order": False
    }
    create_response = client.post("/api/orders", json=order_data, headers=headers)
    assert create_response.status_code == 201
    order_id = create_response.json()["id"]

    # Get the order
    response = client.get(f"/api/orders/{order_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == order_id
    assert data["user_id"] == test_user.id

def test_get_order_by_number(client: Client, db_session: Session, test_user: User):
    """Test getting an order by order number"""
    # Login as test user
    token = create_access_token(data={"sub": test_user.email})
    headers = {"Authorization": f"Bearer {token}"}

    # Create order first
    order_data = {
        "customer_name": "Test Customer",
        "is_group_order": False
    }
    create_response = client.post("/api/orders", json=order_data, headers=headers)
    assert create_response.status_code == 201
    order_number = create_response.json()["order_number"]

    # Get the order by number
    response = client.get(f"/api/orders/number/{order_number}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["order_number"] == order_number
    assert data["user_id"] == test_user.id

def test_get_user_orders(client: Client, db_session: Session, test_user: User):
    """Test getting all orders for a user"""
    # Login as test user
    token = create_access_token(data={"sub": test_user.email})
    headers = {"Authorization": f"Bearer {token}"}

    # Create a few orders
    for i in range(3):
        order_data = {
            "customer_name": f"Test Customer {i}",
            "is_group_order": i % 2 == 0
        }
        response = client.post("/api/orders", json=order_data, headers=headers)
        assert response.status_code == 201

    # Get all orders
    response = client.get("/api/orders", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3  # At least the 3 we just created
    for order in data:
        assert order["user_id"] == test_user.id

def test_update_order(client: Client, db_session: Session, test_user: User):
    """Test updating an order"""
    # Login as test user
    token = create_access_token(data={"sub": test_user.email})
    headers = {"Authorization": f"Bearer {token}"}

    # Create order first
    order_data = {
        "customer_name": "Test Customer",
        "is_group_order": False
    }
    create_response = client.post("/api/orders", json=order_data, headers=headers)
    assert create_response.status_code == 201
    order_id = create_response.json()["id"]

    # Update the order
    update_data = {
        "status": "in_progress"
    }
    response = client.put(f"/api/orders/{order_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == order_id
    assert data["status"] == "in_progress"

def test_cancel_order(client: Client, db_session: Session, test_user: User):
    """Test cancelling an order"""
    # Login as test user
    token = create_access_token(data={"sub": test_user.email})
    headers = {"Authorization": f"Bearer {token}"}

    # Create order first
    order_data = {
        "customer_name": "Test Customer",
        "is_group_order": False
    }
    create_response = client.post("/api/orders", json=order_data, headers=headers)
    assert create_response.status_code == 201
    order_id = create_response.json()["id"]

    # Cancel the order
    response = client.post(f"/api/orders/{order_id}/cancel", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == order_id
    assert data["status"] == "cancelled"

def test_guest_user_order(client: Client, db_session: Session):
    """Test that guest users can create orders"""
    # Create a guest user first
    guest_response = client.post("/api/users/guest-login")
    assert guest_response.status_code == 200
    guest_data = guest_response.json()
    token = guest_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create order as guest user
    order_data = {
        "customer_name": "Guest Customer",
        "is_group_order": False
    }
    response = client.post("/api/orders", json=order_data, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["user_id"] == guest_data["user"]["id"]
    assert data["customer_name"] == order_data["customer_name"]
    assert data["is_group_order"] == order_data["is_group_order"]
    assert "order_number" in data
    assert "table_number" in data
    assert data["status"] == "initialized"

    # Verify guest user can retrieve their order
    get_response = client.get(f"/api/orders/{data['id']}", headers=headers)
    assert get_response.status_code == 200
    get_data = get_response.json()
    assert get_data["id"] == data["id"]
    assert get_data["user_id"] == guest_data["user"]["id"] 