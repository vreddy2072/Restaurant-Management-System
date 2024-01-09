from typing import List

def test_create_category(client):
    response = client.post(
        "/api/menu/categories/",
        json={"name": "Test Category", "description": "Test Description"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Category"
    assert data["description"] == "Test Description"
    assert data["is_active"] == True

def test_create_duplicate_category(client, db_session, sample_category):
    # Get the category name from the database
    from backend.models.orm.menu import Category
    category = db_session.query(Category).filter(Category.id == sample_category).first()
    response = client.post(
        "/api/menu/categories/",
        json={"name": category.name}
    )
    assert response.status_code == 400

def test_get_categories(client, db_session, sample_category):
    # Get the category from the database
    from backend.models.orm.menu import Category
    category = db_session.query(Category).filter(Category.id == sample_category).first()
    response = client.get("/api/menu/categories/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["name"] == category.name

def test_get_category(client, db_session, sample_category):
    # Get the category from the database
    from backend.models.orm.menu import Category
    category = db_session.query(Category).filter(Category.id == sample_category).first()
    response = client.get(f"/api/menu/categories/{sample_category}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_category
    assert data["name"] == category.name

def test_update_category(client, sample_category):
    response = client.put(
        f"/api/menu/categories/{sample_category}",
        json={"name": "Updated Category"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Category"

def test_delete_category(client, sample_category):
    response = client.delete(f"/api/menu/categories/{sample_category}")
    assert response.status_code == 200
    
    # Verify category is inactive
    response = client.get(f"/api/menu/categories/{sample_category}")
    assert response.status_code == 200
    assert response.json()["is_active"] == False

def test_create_menu_item(client, db_session, sample_category):
    response = client.post(
        "/api/menu/items/",
        json={
            "name": "Test Item",
            "description": "Test Description",
            "price": 9.99,
            "category_id": sample_category,
            "is_vegetarian": True,
            "spice_level": 1,
            "preparation_time": 15
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Item"
    assert data["price"] == 9.99
    assert data["category_id"] == sample_category

def test_create_menu_item_invalid_category(client):
    response = client.post(
        "/api/menu/items/",
        json={
            "name": "Test Item",
            "price": 9.99,
            "category_id": 999
        }
    )
    assert response.status_code == 404

def test_get_menu_items(client, sample_menu_item):
    response = client.get("/api/menu/items/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["name"] == sample_menu_item.name

def test_get_menu_items_by_category(client, sample_menu_item, sample_category):
    response = client.get(f"/api/menu/items/?category_id={sample_category}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["category_id"] == sample_category

def test_update_menu_item(client, sample_menu_item):
    response = client.put(
        f"/api/menu/items/{sample_menu_item.id}",
        json={
            "name": "Updated Item",
            "price": 14.99,
            "category_id": sample_menu_item.category_id
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Item"
    assert data["price"] == 14.99

def test_delete_menu_item(client, sample_menu_item):
    item_id = sample_menu_item.id
    response = client.delete(f"/api/menu/items/{item_id}")
    assert response.status_code == 200
    
    # Verify item is inactive
    response = client.get(f"/api/menu/items/{item_id}")
    assert response.status_code == 200
    assert response.json()["is_active"] == False

def test_get_full_menu(client, sample_category, sample_menu_item):
    response = client.get("/api/menu/")
    assert response.status_code == 200
    data = response.json()
    assert len(data["categories"]) > 0
    assert len(data["categories"][0]["menu_items"]) > 0
    assert data["categories"][0]["menu_items"][0]["id"] == sample_menu_item.id

def test_create_menu_item_with_allergens(client, sample_category):
    # Create allergens
    allergens_data = [
        {"name": "Gluten", "description": "Wheat and gluten"},
        {"name": "Sesame", "description": "Sesame seeds"}
    ]
    allergen_ids = []
    for allergen in allergens_data:
        response = client.post("/menu/allergens/", json=allergen)
        allergen_ids.append(response.json()["id"])
    
    # Create menu item with allergens
    menu_item_data = {
        "name": "Sesame Bread",
        "description": "Fresh bread with sesame seeds",
        "price": 3.99,
        "category_id": sample_category,
        "allergen_ids": allergen_ids,
        "customization_options": {
            "size": ["small", "medium", "large"],
            "toasting": ["light", "medium", "dark"]
        }
    }
    
    response = client.post("/menu/menu-items/", json=menu_item_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Sesame Bread"
    assert len(data["allergens"]) == 2
    assert all(allergen["name"] in ["Gluten", "Sesame"] for allergen in data["allergens"])
    assert "size" in data["customization_options"]
    assert "toasting" in data["customization_options"]

def test_update_menu_item_allergens(client, sample_category):
    # Create allergens
    allergens_data = [
        {"name": "Milk", "description": "Dairy products"},
        {"name": "Nuts", "description": "Tree nuts"}
    ]
    allergen_ids = []
    for allergen in allergens_data:
        response = client.post("/menu/allergens/", json=allergen)
        allergen_ids.append(response.json()["id"])
    
    # Create menu item
    menu_item_data = {
        "name": "Nutty Ice Cream",
        "description": "Ice cream with nuts",
        "price": 5.99,
        "category_id": sample_category,
        "allergen_ids": [allergen_ids[0]]  # Only milk allergen initially
    }
    
    create_response = client.post("/menu/menu-items/", json=menu_item_data)
    menu_item_id = create_response.json()["id"]
    assert create_response.status_code == 201  # Created status code
    
    # Update menu item to add nut allergen
    update_data = {
        "allergen_ids": allergen_ids  # Both milk and nuts
    }
    
    response = client.put(f"/menu/menu-items/{menu_item_id}", json=update_data)
    assert response.status_code == 200
    updated_data = response.json()
    assert len(updated_data["allergens"]) == 2
    assert all(allergen["name"] in ["Milk", "Nuts"] for allergen in updated_data["allergens"])

def test_filter_menu_items(client, sample_category):
    # Create menu items with different properties
    menu_items = [
        {
            "name": "Vegan Salad",
            "description": "Fresh vegan salad",
            "price": 8.99,
            "category_id": sample_category,
            "is_vegan": True,
            "is_vegetarian": True,
            "is_gluten_free": True
        },
        {
            "name": "Chicken Pasta",
            "description": "Creamy chicken pasta",
            "price": 12.99,
            "category_id": sample_category,
            "is_vegan": False,
            "is_vegetarian": False,
            "is_gluten_free": False
        },
        {
            "name": "Vegetable Soup",
            "description": "Healthy vegetable soup",
            "price": 6.99,
            "category_id": sample_category,
            "is_vegan": True,
            "is_vegetarian": True,
            "is_gluten_free": True
        }
    ]
    
    for item in menu_items:
        client.post("/menu/menu-items/", json=item)
    
    # Test various filters
    # Filter by dietary preferences
    response = client.get("/menu/menu-items/filter", params={"is_vegan": True})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(item["is_vegan"] for item in data)
    
    # Filter by price range
    response = client.get("/menu/menu-items/filter", params={"min_price": 10.0})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Chicken Pasta"
    
    # Filter by multiple criteria
    response = client.get("/menu/menu-items/filter", params={
        "is_vegetarian": True,
        "is_gluten_free": True,
        "max_price": 7.0
    })
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Vegetable Soup" 

def test_menu_item_rating_update(client, sample_menu_item):
    # Update menu item with initial rating
    response = client.put(
        f"/menu/items/{sample_menu_item.id}",
        json={
            "average_rating": 4.5,
            "rating_count": 1
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["average_rating"] == 4.5
    assert data["rating_count"] == 1

    # Add another rating
    response = client.put(
        f"/menu/items/{sample_menu_item.id}",
        json={
            "average_rating": 4.0,  # (4.5 + 3.5) / 2
            "rating_count": 2
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["average_rating"] == 4.0
    assert data["rating_count"] == 2

def test_menu_item_invalid_customization(client, sample_category):
    # Try to create menu item with invalid customization format
    response = client.post(
        "/menu/items/",
        json={
            "name": "Test Item",
            "description": "Test Description",
            "price": 9.99,
            "category_id": sample_category,
            "customization_options": "invalid"  # Should be a dict
        }
    )
    assert response.status_code == 422  # Validation error

    # Try with invalid customization structure
    response = client.post(
        "/menu/items/",
        json={
            "name": "Test Item",
            "description": "Test Description",
            "price": 9.99,
            "category_id": sample_category,
            "customization_options": {
                "size": "small"  # Should be a list
            }
        }
    )
    assert response.status_code == 422  # Validation error

def test_filter_menu_items_multiple_allergens(client, sample_category):
    # Create allergens
    allergens = [
        {"name": "Dairy", "description": "Milk products"},
        {"name": "Nuts", "description": "Tree nuts"},
        {"name": "Soy", "description": "Soy products"}
    ]
    allergen_ids = []
    for allergen in allergens:
        response = client.post("/menu/allergens/", json=allergen)
        assert response.status_code == 201
        allergen_ids.append(response.json()["id"])
    
    # Create menu items with different allergen combinations
    menu_items = [
        {
            "name": "Item 1",
            "description": "Test item 1",
            "price": 9.99,
            "category_id": sample_category,
            "allergen_ids": allergen_ids[:2]  # Dairy and Nuts
        },
        {
            "name": "Item 2",
            "description": "Test item 2",
            "price": 9.99,
            "category_id": sample_category,
            "allergen_ids": allergen_ids[1:]  # Nuts and Soy
        },
        {
            "name": "Item 3",
            "description": "Test item 3",
            "price": 9.99,
            "category_id": sample_category,
            "allergen_ids": []  # No allergens
        }
    ]
    
    for item in menu_items:
        response = client.post("/menu/menu-items/", json=item)
        assert response.status_code == 201
    
    # Test excluding multiple allergens
    response = client.get(
        "/menu/menu-items/filter",
        params={"allergen_exclude_ids": allergen_ids[:2]}  # Exclude Dairy and Nuts
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Item 3"

    # Test excluding single allergen
    response = client.get(
        "/menu/menu-items/filter",
        params={"allergen_exclude_ids": [allergen_ids[0]]}  # Exclude only Dairy
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(item["name"] in ["Item 2", "Item 3"] for item in data) 

def test_update_category_put(client, sample_category):
    response = client.put(
        f"/api/menu/categories/{sample_category}",
        json={"name": "Updated Category"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Category"

def test_update_category_patch(client, sample_category):
    response = client.patch(
        f"/api/menu/categories/{sample_category}",
        json={"name": "Patched Category"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Patched Category"

def test_update_menu_item_put(client, sample_menu_item):
    response = client.put(
        f"/api/menu/items/{sample_menu_item.id}",
        json={
            "name": "Updated Item",
            "price": 14.99,
            "category_id": sample_menu_item.category_id
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Item"
    assert data["price"] == 14.99

def test_update_menu_item_patch(client, sample_menu_item):
    response = client.patch(
        f"/api/menu/items/{sample_menu_item.id}",
        json={
            "name": "Patched Item",
            "price": 16.99
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Patched Item"
    assert data["price"] == 16.99 

def test_upload_menu_item_image(client, sample_menu_item):
    # Create a test image file
    image_content = b"fake image content"
    files = {
        "file": ("test_image.jpg", image_content, "image/jpeg")
    }
    
    response = client.post(
        f"/api/menu/items/{sample_menu_item.id}/image",
        files=files
    )
    assert response.status_code == 200
    data = response.json()
    assert data["image_url"].startswith("/static/images/")
    assert data["image_url"].endswith(".jpg")

def test_upload_menu_item_image_invalid_file(client, sample_menu_item):
    # Try to upload a non-image file
    files = {
        "file": ("test.txt", b"not an image", "text/plain")
    }
    
    response = client.post(
        f"/api/menu/items/{sample_menu_item.id}/image",
        files=files
    )
    assert response.status_code == 400
    assert "must be an image" in response.json()["detail"] 