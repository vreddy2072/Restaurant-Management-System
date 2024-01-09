import pytest
from httpx import Client
from sqlalchemy.orm import Session
import logging

from backend.models.orm.user import User
from backend.models.orm.menu import MenuItem
from backend.services.user_service import UserService
from backend.utils.auth import create_access_token

pytestmark = pytest.mark.usefixtures("db_session")

def test_get_cart_unauthorized(client: Client):
    """Test that unauthorized users cannot access cart"""
    response = client.get("/api/cart")
    assert response.status_code == 401

def test_get_cart(client: Client, db_session: Session, test_user: User):
    """Test getting a user's cart"""
    # Login as test user
    token = create_access_token(data={"sub": test_user.email})
    headers = {"Authorization": f"Bearer {token}"}

    # Get cart (should be created if it doesn't exist)
    response = client.get("/api/cart", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["user_id"] == test_user.id
    assert "items" in data

def test_add_item_to_cart(
    client: Client,
    db_session: Session,
    test_user: User,
    test_menu_item: MenuItem
):
    """Test adding an item to the cart"""
    # Login as test user
    token = create_access_token(data={"sub": test_user.email})
    headers = {"Authorization": f"Bearer {token}"}

    # Add item to cart
    item_data = {
        "menu_item_id": test_menu_item.id,
        "quantity": 2,
        "customizations": {"notes": "Extra spicy"}
    }
    response = client.post(
        "/api/cart/items",
        headers=headers,
        json=item_data
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) > 0
    cart_item = next(item for item in data["items"] if item["menu_item_id"] == test_menu_item.id)
    assert cart_item["quantity"] == 2
    assert cart_item["customizations"] == {"notes": "Extra spicy"}

def test_add_invalid_item_to_cart(
    client: Client,
    db_session: Session,
    test_user: User
):
    """Test adding an invalid item to the cart"""
    # Login as test user
    token = create_access_token(data={"sub": test_user.email})
    headers = {"Authorization": f"Bearer {token}"}

    # Try to add non-existent menu item
    item_data = {
        "menu_item_id": 9999,
        "quantity": 1
    }
    response = client.post(
        "/api/cart/items",
        headers=headers,
        json=item_data
    )
    assert response.status_code == 400

def test_update_cart_item(
    client: Client,
    db_session: Session,
    test_user: User,
    test_menu_item: MenuItem
):
    """Test updating a cart item"""
    # Login as test user
    token = create_access_token(data={"sub": test_user.email})
    headers = {"Authorization": f"Bearer {token}"}

    # Add item to cart
    item_data = {
        "menu_item_id": test_menu_item.id,
        "quantity": 1
    }
    response = client.post(
        "/api/cart/items",
        headers=headers,
        json=item_data
    )
    assert response.status_code == 200
    data = response.json()
    cart_item = next(item for item in data["items"] if item["menu_item_id"] == test_menu_item.id)
    item_id = cart_item["id"]

    # Update item quantity
    update_data = {"quantity": 3}
    response = client.put(
        f"/api/cart/items/{item_id}",
        headers=headers,
        json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    cart_item = next(item for item in data["items"] if item["id"] == item_id)
    assert cart_item["quantity"] == 3

def test_remove_cart_item(
    client: Client,
    db_session: Session,
    test_user: User,
    test_menu_item: MenuItem
):
    """Test removing an item from the cart"""
    # Login as test user
    token = create_access_token(data={"sub": test_user.email})
    headers = {"Authorization": f"Bearer {token}"}

    # Add item to cart
    item_data = {
        "menu_item_id": test_menu_item.id,
        "quantity": 1
    }
    response = client.post(
        "/api/cart/items",
        headers=headers,
        json=item_data
    )
    assert response.status_code == 200
    data = response.json()
    cart_item = next(item for item in data["items"] if item["menu_item_id"] == test_menu_item.id)
    item_id = cart_item["id"]

    # Remove item
    response = client.delete(f"/api/cart/items/{item_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert not any(item["id"] == item_id for item in data["items"])

def test_clear_cart(
    client: Client,
    db_session: Session,
    test_user: User,
    test_menu_item: MenuItem
):
    """Test clearing the entire cart"""
    # Login as test user
    token = create_access_token(data={"sub": test_user.email})
    headers = {"Authorization": f"Bearer {token}"}

    # Add items to cart
    item_data = {
        "menu_item_id": test_menu_item.id,
        "quantity": 2
    }
    client.post(
        "/api/cart/items",
        headers=headers,
        json=item_data
    )

    # Clear cart
    response = client.delete("/api/cart", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 0

    # Verify cart is empty
    response = client.get("/api/cart", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 0

def test_get_cart_total(
    client: Client,
    db_session: Session,
    test_user: User,
    test_menu_item: MenuItem
):
    """Test calculating cart total"""
    # Login as test user
    token = create_access_token(data={"sub": test_user.email})
    headers = {"Authorization": f"Bearer {token}"}

    # Add item to cart
    item_data = {
        "menu_item_id": test_menu_item.id,
        "quantity": 2
    }
    client.post(
        "/api/cart/items",
        headers=headers,
        json=item_data
    )

    # Get cart total
    response = client.get("/api/cart/total", headers=headers)
    assert response.status_code == 200
    total = float(response.json())
    assert total == test_menu_item.price * 2
