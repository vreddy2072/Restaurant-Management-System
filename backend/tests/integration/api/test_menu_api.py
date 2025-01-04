from typing import List

def test_create_category(client):
    response = client.post(
        "/api/menu/categories/",
        json={"name": "Test Category", "description": "Test Description"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Category"
    assert data["description"] == "Test Description"
    assert data["is_active"] == True

def test_create_duplicate_category(client, db_session, sample_category):
    # Get the category name from the database
    from backend.models.orm.menu import Category
    category = db_session.query(Category).filter(Category.id == sample_category.id).first()
    response = client.post(
        "/api/menu/categories/",
        json={"name": category.name}
    )
    assert response.status_code == 400

def test_get_categories(client, db_session, sample_category):
    response = client.get("/api/menu/categories/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert all(isinstance(item, dict) for item in data)
    assert all("name" in item for item in data)

def test_get_category(client, db_session, sample_category):
    response = client.get(f"/api/menu/categories/{sample_category.id}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "name" in data
    assert "description" in data

def test_update_category(client, sample_category):
    response = client.put(
        f"/api/menu/categories/{sample_category.id}",
        json={"name": "Updated Category", "description": "Updated Description"}
    )
    assert response.status_code == 200

def test_delete_category(client, sample_category):
    response = client.delete(f"/api/menu/categories/{sample_category.id}")
    assert response.status_code == 200
    get_response = client.get(f"/api/menu/categories/{sample_category.id}")
    assert get_response.status_code == 404

def test_create_menu_item(client, db_session, sample_category):
    response = client.post(
        "/api/menu/items/",
        json={
            "name": "Test Item",
            "description": "Test Description",
            "price": 9.99,
            "category_id": sample_category.id,
            "is_vegetarian": True,
            "spice_level": 1
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Item"
    assert data["price"] == 9.99
    assert data["category_id"] == sample_category.id

def test_create_menu_item_invalid_category(client):
    response = client.post(
        "/api/menu/items/",
        json={
            "name": "Test Item",
            "description": "Test Description",
            "price": 9.99,
            "category_id": 999999  # Invalid category ID
        }
    )
    assert response.status_code == 400

def test_get_menu_items(client, sample_menu_item):
    response = client.get("/api/menu/items/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_menu_items_by_category(client, sample_menu_item, sample_category):
    response = client.get(f"/api/menu/items/?category_id={sample_category.id}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_update_menu_item(client, sample_menu_item):
    response = client.put(
        f"/api/menu/items/{sample_menu_item.id}",
        json={
            "name": "Updated Item",
            "description": "Updated Description",
            "price": 15.99
        }
    )
    assert response.status_code == 200

def test_delete_menu_item(client, sample_menu_item):
    response = client.delete(f"/api/menu/items/{sample_menu_item.id}")
    assert response.status_code == 200
    get_response = client.get(f"/api/menu/items/{sample_menu_item.id}")
    assert get_response.status_code == 404

def test_get_full_menu(client, sample_category, sample_menu_item):
    response = client.get("/api/menu/full")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_create_menu_item_with_allergens(client, sample_category):
    # Create allergens first
    allergen1_response = client.post(
        "/api/menu/allergens/",
        json={"name": "Peanuts", "description": "Tree nuts"}
    )
    assert allergen1_response.status_code == 201
    allergen1_id = allergen1_response.json()["id"]

    allergen2_response = client.post(
        "/api/menu/allergens/",
        json={"name": "Dairy", "description": "Milk products"}
    )
    assert allergen2_response.status_code == 201
    allergen2_id = allergen2_response.json()["id"]

    # Create menu item with allergens
    response = client.post(
        "/api/menu/items/",
        json={
            "name": "Allergen Test Item",
            "description": "Test Description",
            "price": 12.99,
            "category_id": sample_category.id,
            "allergen_ids": [allergen1_id, allergen2_id]
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert len(data["allergens"]) == 2

def test_update_menu_item_allergens(client, sample_category):
    # Create allergens first
    allergen1_response = client.post(
        "/api/menu/allergens/",
        json={"name": "Soy", "description": "Soy products"}
    )
    assert allergen1_response.status_code == 201
    allergen1_id = allergen1_response.json()["id"]

    allergen2_response = client.post(
        "/api/menu/allergens/",
        json={"name": "Eggs", "description": "Egg products"}
    )
    assert allergen2_response.status_code == 201
    allergen2_id = allergen2_response.json()["id"]

    # Create menu item
    menu_item_response = client.post(
        "/api/menu/items/",
        json={
            "name": "Update Allergen Test",
            "description": "Test Description",
            "price": 14.99,
            "category_id": sample_category.id,
            "allergen_ids": [allergen1_id]
        }
    )
    assert menu_item_response.status_code == 201
    menu_item_id = menu_item_response.json()["id"]

    # Update menu item allergens
    response = client.patch(
        f"/api/menu/items/{menu_item_id}",
        json={"allergen_ids": [allergen1_id, allergen2_id]}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["allergens"]) == 2

def test_filter_menu_items(client, sample_category):
    # Create menu items with different properties
    item1_response = client.post(
        "/api/menu/items/",
        json={
            "name": "Vegetarian Item",
            "description": "Vegetarian dish",
            "price": 12.99,
            "category_id": sample_category.id,
            "is_vegetarian": True,
            "is_vegan": False,
            "is_gluten_free": False
        }
    )
    assert item1_response.status_code == 201

    item2_response = client.post(
        "/api/menu/items/",
        json={
            "name": "Vegan Item",
            "description": "Vegan dish",
            "price": 14.99,
            "category_id": sample_category.id,
            "is_vegetarian": True,
            "is_vegan": True,
            "is_gluten_free": True
        }
    )
    assert item2_response.status_code == 201

    # Test filtering
    response = client.get("/api/menu/items/filter?is_vegetarian=true")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

    response = client.get("/api/menu/items/filter?is_vegan=true")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1

def test_menu_item_rating_update(client, sample_menu_item):
    # Update rating
    response = client.post(
        f"/api/menu/items/{sample_menu_item.id}/rate",
        json={"rating": 4.5}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["average_rating"] > 0
    assert data["rating_count"] == 1

def test_menu_item_invalid_customization(client, sample_category):
    # Try to create menu item with invalid customization options
    response = client.post(
        "/api/menu/items/",
        json={
            "name": "Custom Item",
            "description": "Customizable dish",
            "price": 16.99,
            "category_id": sample_category.id,
            "customization_options": {
                "size": ["small", "medium", "large"],
                "toppings": ["cheese", "mushrooms", "pepperoni"]
            }
        }
    )
    assert response.status_code == 201

    # Try invalid customization
    response = client.post(
        f"/api/menu/items/{response.json()['id']}/customize",
        json={
            "size": "extra-large",  # Invalid size
            "toppings": ["cheese"]
        }
    )
    assert response.status_code == 400

def test_filter_menu_items_multiple_allergens(client, sample_category):
    # Create allergens
    allergen1_response = client.post(
        "/api/menu/allergens/",
        json={"name": "Fish", "description": "Fish and seafood"}
    )
    assert allergen1_response.status_code == 201
    allergen1_id = allergen1_response.json()["id"]

    allergen2_response = client.post(
        "/api/menu/allergens/",
        json={"name": "Shellfish", "description": "Shellfish products"}
    )
    assert allergen2_response.status_code == 201
    allergen2_id = allergen2_response.json()["id"]

    # Create menu items with different allergens
    item1_response = client.post(
        "/api/menu/items/",
        json={
            "name": "Fish Dish",
            "description": "Contains fish",
            "price": 18.99,
            "category_id": sample_category.id,
            "allergen_ids": [allergen1_id]
        }
    )
    assert item1_response.status_code == 201

    item2_response = client.post(
        "/api/menu/items/",
        json={
            "name": "Seafood Platter",
            "description": "Contains fish and shellfish",
            "price": 24.99,
            "category_id": sample_category.id,
            "allergen_ids": [allergen1_id, allergen2_id]
        }
    )
    assert item2_response.status_code == 201

    # Test filtering by multiple allergens
    response = client.get(f"/api/menu/items/filter?allergen_exclude_ids={allergen1_id},{allergen2_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0

def test_update_category_put(client, sample_category):
    response = client.put(
        f"/api/menu/categories/{sample_category.id}",
        json={"name": "New Name", "description": "New Description"}
    )
    assert response.status_code == 200

def test_update_category_patch(client, sample_category):
    response = client.patch(
        f"/api/menu/categories/{sample_category.id}",
        json={"description": "Updated Description Only"}
    )
    assert response.status_code == 200

def test_update_menu_item_put(client, sample_menu_item):
    response = client.put(
        f"/api/menu/items/{sample_menu_item.id}",
        json={
            "name": "New Name",
            "description": "New Description",
            "price": 20.99,
            "is_vegetarian": True
        }
    )
    assert response.status_code == 200

def test_update_menu_item_patch(client, sample_menu_item):
    response = client.patch(
        f"/api/menu/items/{sample_menu_item.id}",
        json={"price": 21.99}
    )
    assert response.status_code == 200

def test_upload_menu_item_image(client, sample_menu_item):
    # Create a test image file
    import io
    from PIL import Image

    # Create a small test image
    img = Image.new('RGB', (100, 100), color='red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()

    files = {'file': ('test.png', img_byte_arr, 'image/png')}
    response = client.post(f"/api/menu/items/{sample_menu_item.id}/image", files=files)
    assert response.status_code == 200
    assert "image_url" in response.json()
    assert response.json()["image_url"].startswith("/static/images/")

def test_upload_menu_item_image_invalid_file(client, sample_menu_item):
    # Try to upload an invalid file
    files = {'file': ('test.txt', b'not an image', 'text/plain')}
    response = client.post(f"/api/menu/items/{sample_menu_item.id}/image", files=files)
    assert response.status_code == 400
    assert "File must be an image" in response.json()["detail"]
