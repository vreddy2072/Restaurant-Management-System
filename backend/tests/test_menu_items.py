def test_create_menu_item_with_allergens():
    response = client.post(
        "/api/menu/items/",
        json={
            "name": "Test Item",
            "description": "Test Description",
            "price": 9.99,
            "category_id": 1,
            "is_active": True,
            "allergens": ["dairy", "nuts"]
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert "allergens" in data
    assert set(data["allergens"]) == {"dairy", "nuts"}

def test_update_menu_item_allergens():
    # First create an item
    create_response = client.post(
        "/api/menu/items/",
        json={
            "name": "Test Item",
            "description": "Test Description",
            "price": 9.99,
            "category_id": 1,
            "allergens": ["dairy"]
        }
    )
    item_id = create_response.json()["id"]

    # Then update its allergens
    update_response = client.patch(
        f"/api/menu/items/{item_id}",
        json={
            "allergens": ["dairy", "nuts"]
        }
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert set(data["allergens"]) == {"dairy", "nuts"} 