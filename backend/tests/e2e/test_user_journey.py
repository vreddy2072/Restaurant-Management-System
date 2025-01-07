import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_complete_user_journey():
    """Test complete user journey from registration to order placement"""
    # 1. Register a new user
    register_response = client.post(
        "/api/users/",
        json={
            "username": "customer1",
            "email": "customer1@example.com",
            "password": "testpassword",
            "first_name": "Test",
            "last_name": "Customer",
            "role": "customer"
        }
    )
    assert register_response.status_code == 201
    user_data = register_response.json()
    assert user_data["username"] == "customer1"

    # 2. Login with the new user
    login_response = client.post(
        "/api/auth/login",
        data={
            "username": "customer1@example.com",
            "password": "testpassword"
        }
    )
    assert login_response.status_code == 200
    token_data = login_response.json()
    access_token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # 3. View menu items
    menu_response = client.get("/api/menu/items", headers=headers)
    assert menu_response.status_code == 200
    menu_items = menu_response.json()

    # 4. Create an order
    if menu_items:
        order_response = client.post(
            "/api/orders/",
            headers=headers,
            json={
                "items": [
                    {
                        "menu_item_id": menu_items[0]["id"],
                        "quantity": 2,
                        "special_instructions": "No onions please"
                    }
                ],
                "delivery_address": "123 Test St, Test City",
                "contact_phone": "1234567890"
            }
        )
        assert order_response.status_code == 201
        order_data = order_response.json()
        order_id = order_data["id"]

        # 5. Check order status
        status_response = client.get(f"/api/orders/{order_id}", headers=headers)
        assert status_response.status_code == 200
        order_status = status_response.json()
        assert order_status["id"] == order_id
        assert order_status["status"] in ["pending", "confirmed"]

def test_admin_journey():
    """Test complete admin journey"""
    # 1. Register admin user (assuming admin creation is allowed in test environment)
    register_response = client.post(
        "/api/users/",
        json={
            "username": "admin1",
            "email": "admin1@example.com",
            "password": "adminpass",
            "first_name": "Admin",
            "last_name": "User",
            "role": "admin"
        }
    )
    assert register_response.status_code == 201

    # 2. Login as admin
    login_response = client.post(
        "/api/auth/login",
        data={
            "username": "admin1@example.com",
            "password": "adminpass"
        }
    )
    assert login_response.status_code == 200
    token_data = login_response.json()
    access_token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # 3. Create a new menu item
    menu_item_response = client.post(
        "/api/menu/items",
        headers=headers,
        json={
            "name": "Test Dish",
            "description": "A test dish",
            "price": 9.99,
            "category": "main",
            "is_vegetarian": True
        }
    )
    assert menu_item_response.status_code == 201
    menu_item = menu_item_response.json()

    # 4. View all orders
    orders_response = client.get("/api/orders/all", headers=headers)
    assert orders_response.status_code == 200

    # 5. Update order status (if any orders exist)
    orders = orders_response.json()
    if orders:
        update_response = client.patch(
            f"/api/orders/{orders[0]['id']}/status",
            headers=headers,
            json={"status": "confirmed"}
        )
        assert update_response.status_code == 200
