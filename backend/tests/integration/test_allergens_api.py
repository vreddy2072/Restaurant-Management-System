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
    assert "already exists" in response.json()["detail"].lower()

def test_get_allergens(client):
    # Create some allergens
    allergens = [
        {"name": "Soy", "description": "Soy and soy products"},
        {"name": "Wheat", "description": "Wheat and gluten"},
        {"name": "Eggs", "description": "Egg and egg products"}
    ]
    for allergen in allergens:
        client.post("/api/menu/allergens/", json=allergen)
    
    response = client.get("/api/menu/allergens/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3
    assert all(item["name"] in [a["name"] for a in allergens] for item in data[:3])

def test_get_allergen(client):
    # Create an allergen
    create_response = client.post(
        "/menu/allergens/",
        json={"name": "Fish", "description": "Fish and fish products"}
    )
    allergen_id = create_response.json()["id"]
    
    # Get the allergen
    response = client.get(f"/menu/allergens/{allergen_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Fish"
    assert data["description"] == "Fish and fish products"

def test_update_allergen_put(client):
    # Create an allergen
    create_response = client.post(
        "/api/menu/allergens/",
        json={"name": "Shellfish", "description": "Shellfish and crustaceans"}
    )
    allergen_id = create_response.json()["id"]
    
    # Update the allergen with PUT
    response = client.put(
        f"/api/menu/allergens/{allergen_id}",
        json={"name": "Crustaceans", "description": "All types of shellfish"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Crustaceans"
    assert data["description"] == "All types of shellfish"

def test_update_allergen_patch(client):
    # Create an allergen
    create_response = client.post(
        "/api/menu/allergens/",
        json={"name": "Shellfish", "description": "Shellfish and crustaceans"}
    )
    allergen_id = create_response.json()["id"]
    
    # Update the allergen with PATCH
    response = client.patch(
        f"/api/menu/allergens/{allergen_id}",
        json={"description": "Updated description"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Shellfish"  # Name should remain unchanged
    assert data["description"] == "Updated description"

def test_delete_allergen(client):
    # Create an allergen
    create_response = client.post(
        "/menu/allergens/",
        json={"name": "Mustard", "description": "Mustard and mustard products"}
    )
    allergen_id = create_response.json()["id"]
    
    # Delete the allergen
    response = client.delete(f"/menu/allergens/{allergen_id}")
    assert response.status_code == 200
    
    # Verify it's deleted
    get_response = client.get(f"/menu/allergens/{allergen_id}")
    assert get_response.status_code == 404

def test_filter_menu_items_by_allergens(client, sample_category):
    # Create allergens
    peanut_response = client.post(
        "/api/menu/allergens/",
        json={"name": "Peanuts", "description": "Peanuts and tree nuts"}
    )
    dairy_response = client.post(
        "/api/menu/allergens/",
        json={"name": "Dairy", "description": "Milk and dairy products"}
    )
    peanut_id = peanut_response.json()["id"]
    dairy_id = dairy_response.json()["id"]
    
    # Create menu items with different allergens
    menu_items = [
        {
            "name": "Peanut Butter Shake",
            "description": "Creamy shake with peanut butter",
            "price": 5.99,
            "category_id": sample_category,
            "allergen_ids": [peanut_id, dairy_id]
        },
        {
            "name": "Milk Shake",
            "description": "Classic milk shake",
            "price": 4.99,
            "category_id": sample_category,
            "allergen_ids": [dairy_id]
        },
        {
            "name": "Fruit Smoothie",
            "description": "Fresh fruit smoothie",
            "price": 4.99,
            "category_id": sample_category,
            "allergen_ids": []
        }
    ]
    
    for item in menu_items:
        client.post("/menu/menu-items/", json=item)
    
    # Test filtering
    response = client.get("/menu/menu-items/filter", params={"allergen_exclude_ids": [peanut_id]})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all("Peanut" not in item["name"] for item in data)
    
    response = client.get("/menu/menu-items/filter", params={"allergen_exclude_ids": [dairy_id]})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Fruit Smoothie" 