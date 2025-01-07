from fastapi.testclient import TestClient
import pytest
from backend.models.orm.menu import Allergen

def test_create_allergen(client):
    response = client.post(
        "/api/menu/allergens/",
        json={"name": "Peanuts", "description": "Tree nuts and peanuts"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Peanuts"
    assert data["description"] == "Tree nuts and peanuts"
    assert "id" in data

def test_create_duplicate_allergen(client):
    # Create first allergen
    client.post(
        "/api/menu/allergens/",
        json={"name": "Dairy", "description": "Milk and dairy products"}
    )
    
    # Try to create duplicate
    response = client.post(
        "/api/menu/allergens/",
        json={"name": "Dairy", "description": "Different description"}
    )
    assert response.status_code == 400

def test_get_allergens(client):
    # Create some allergens first
    client.post("/api/menu/allergens/", json={"name": "Soy", "description": "Soy and derivatives"})
    client.post("/api/menu/allergens/", json={"name": "Gluten", "description": "Wheat and gluten"})
    
    response = client.get("/api/menu/allergens/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    assert all(isinstance(item, dict) for item in data)
    assert all("name" in item for item in data)

def test_get_allergen(client):
    # Create an allergen first
    create_response = client.post(
        "/api/menu/allergens/",
        json={"name": "Eggs", "description": "Eggs and egg products"}
    )
    allergen_id = create_response.json()["id"]
    
    response = client.get(f"/api/menu/allergens/{allergen_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Eggs"
    assert data["description"] == "Eggs and egg products"

def test_update_allergen_put(client):
    # Create an allergen first
    create_response = client.post(
        "/api/menu/allergens/",
        json={"name": "Fish", "description": "Fish and seafood"}
    )
    allergen_id = create_response.json()["id"]
    
    response = client.put(
        f"/api/menu/allergens/{allergen_id}",
        json={"name": "Seafood", "description": "Fish and shellfish"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Seafood"
    assert data["description"] == "Fish and shellfish"

def test_update_allergen_patch(client):
    # Create an allergen first
    create_response = client.post(
        "/api/menu/allergens/",
        json={"name": "Nuts", "description": "Tree nuts"}
    )
    allergen_id = create_response.json()["id"]
    
    response = client.patch(
        f"/api/menu/allergens/{allergen_id}",
        json={"description": "All types of nuts"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Nuts"  # Name unchanged
    assert data["description"] == "All types of nuts"  # Description updated

def test_delete_allergen(client):
    # Create an allergen first
    create_response = client.post(
        "/api/menu/allergens/",
        json={"name": "Mustard", "description": "Mustard and seeds"}
    )
    allergen_id = create_response.json()["id"]
    
    response = client.delete(f"/api/menu/allergens/{allergen_id}")
    assert response.status_code == 200
    
    # Verify it's deleted
    get_response = client.get(f"/api/menu/allergens/{allergen_id}")
    assert get_response.status_code == 404

def test_filter_menu_items_by_allergens(client, sample_category):
    # Create allergens
    allergen1_response = client.post(
        "/api/menu/allergens/",
        json={"name": "Milk", "description": "Dairy products"}
    )
    allergen1_id = allergen1_response.json()["id"]

    allergen2_response = client.post(
        "/api/menu/allergens/",
        json={"name": "Wheat", "description": "Wheat products"}
    )
    allergen2_id = allergen2_response.json()["id"]

    # Create menu items with different allergens
    client.post(
        "/api/menu/items/",
        json={
            "name": "Cheese Pizza",
            "description": "Classic cheese pizza",
            "price": 10.99,
            "category_id": sample_category.id,
            "allergen_ids": [allergen1_id, allergen2_id]
        }
    )

    # Create another menu item with only one allergen
    client.post(
        "/api/menu/items/",
        json={
            "name": "Gluten-Free Pizza",
            "description": "Pizza with gluten-free crust",
            "price": 12.99,
            "category_id": sample_category.id,
            "allergen_ids": [allergen1_id]
        }
    )

    # Test filtering by allergens
    response = client.get(f"/api/menu/items/filter?allergen_exclude_ids={allergen2_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Gluten-Free Pizza"
