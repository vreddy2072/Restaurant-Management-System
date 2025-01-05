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

def test_rate_menu_item(client, sample_menu_item):
    """Test rating a menu item"""
    # Initial rating
    response = client.post(
        f"/api/menu/items/{sample_menu_item.id}/rate",
        json={"rating": 4.5}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["average_rating"] == 4.5
    assert data["rating_count"] == 1

    # Add another rating
    response = client.post(
        f"/api/menu/items/{sample_menu_item.id}/rate",
        json={"rating": 3.5}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["average_rating"] == 4.0  # (4.5 + 3.5) / 2
    assert data["rating_count"] == 2

def test_rate_inactive_menu_item(client, sample_menu_item):
    """Test rating an inactive menu item"""
    # Delete (deactivate) the menu item
    client.delete(f"/api/menu/items/{sample_menu_item.id}")
    
    # Try to rate it
    response = client.post(
        f"/api/menu/items/{sample_menu_item.id}/rate",
        json={"rating": 4.5}
    )
    assert response.status_code == 404

def test_customize_menu_item(client, sample_menu_item):
    """Test customizing a menu item with valid options"""
    # First update the menu item to have customization options
    client.patch(
        f"/api/menu/items/{sample_menu_item.id}",
        json={
            "customization_options": {
                "size": ["small", "medium", "large"],
                "spice_level": ["mild", "medium", "hot"]
            }
        }
    )
    
    # Test valid customization
    response = client.post(
        f"/api/menu/items/{sample_menu_item.id}/customize",
        json={
            "size": "medium",
            "spice_level": "hot"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["selected_customization"] == {
        "size": "medium",
        "spice_level": "hot"
    }

def test_customize_menu_item_invalid_options(client, sample_menu_item):
    """Test customizing a menu item with invalid options"""
    # First update the menu item to have customization options
    client.patch(
        f"/api/menu/items/{sample_menu_item.id}",
        json={
            "customization_options": {
                "size": ["small", "medium", "large"]
            }
        }
    )
    
    # Test invalid option
    response = client.post(
        f"/api/menu/items/{sample_menu_item.id}/customize",
        json={
            "size": "extra-large"  # Invalid size
        }
    )
    assert response.status_code == 400
    assert "Invalid value" in response.json()["detail"]

def test_customize_menu_item_no_options(client, sample_menu_item):
    """Test customizing a menu item that doesn't support customization"""
    response = client.post(
        f"/api/menu/items/{sample_menu_item.id}/customize",
        json={
            "size": "medium"
        }
    )
    assert response.status_code == 400
    assert "does not support customization" in response.json()["detail"]

def test_filter_menu_items_price_range(client, sample_category):
    """Test filtering menu items by price range"""
    # Create menu items with different prices
    items = [
        {"name": "Cheap Item", "price": 5.99},
        {"name": "Medium Item", "price": 15.99},
        {"name": "Expensive Item", "price": 25.99}
    ]
    
    for item in items:
        client.post(
            "/api/menu/items/",
            json={
                **item,
                "category_id": sample_category.id
            }
        )
    
    # Test price range filter
    response = client.get("/api/menu/menu-items/filter?min_price=10&max_price=20")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Medium Item"

def test_filter_menu_items_by_rating(client, sample_category):
    """Test filtering menu items by rating"""
    # Create a menu item
    response = client.post(
        "/api/menu/items/",
        json={
            "name": "Rated Item",
            "price": 9.99,
            "category_id": sample_category.id
        }
    )
    item_id = response.json()["id"]
    
    # Add some ratings
    client.post(f"/api/menu/items/{item_id}/rate", json={"rating": 4.5})
    client.post(f"/api/menu/items/{item_id}/rate", json={"rating": 4.7})
    
    # Test rating filter
    response = client.get("/api/menu/menu-items/filter?min_rating=4.0")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Rated Item"
    assert data[0]["average_rating"] > 4.0

def test_allergen_management(client):
    """Test CRUD operations for allergens"""
    # Create allergen
    create_response = client.post(
        "/api/menu/allergens/",
        json={
            "name": "Test Allergen",
            "description": "Test Description"
        }
    )
    assert create_response.status_code == 201
    allergen_id = create_response.json()["id"]
    
    # Get allergen
    get_response = client.get(f"/api/menu/allergens/{allergen_id}")
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Test Allergen"
    
    # Update allergen
    update_response = client.put(
        f"/api/menu/allergens/{allergen_id}",
        json={
            "name": "Updated Allergen",
            "description": "Updated Description"
        }
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Updated Allergen"
    
    # Patch allergen
    patch_response = client.patch(
        f"/api/menu/allergens/{allergen_id}",
        json={"description": "Patched Description"}
    )
    assert patch_response.status_code == 200
    assert patch_response.json()["description"] == "Patched Description"
    
    # List allergens
    list_response = client.get("/api/menu/allergens/")
    assert list_response.status_code == 200
    assert len(list_response.json()) > 0
    
    # Delete allergen
    delete_response = client.delete(f"/api/menu/allergens/{allergen_id}")
    assert delete_response.status_code == 200
    
    # Verify deletion
    get_deleted = client.get(f"/api/menu/allergens/{allergen_id}")
    assert get_deleted.status_code == 404

def test_filter_menu_items_combined_filters(client, sample_category):
    """Test filtering menu items with multiple criteria"""
    # Create allergens
    allergen_response = client.post(
        "/api/menu/allergens/",
        json={"name": "Test Allergen", "description": "Test"}
    )
    allergen_id = allergen_response.json()["id"]
    
    # Create menu items with various properties
    items = [
        {
            "name": "Perfect Match",
            "price": 15.99,
            "is_vegetarian": True,
            "is_gluten_free": True,
            "allergen_ids": []
        },
        {
            "name": "Almost Match",
            "price": 15.99,
            "is_vegetarian": True,
            "is_gluten_free": False,
            "allergen_ids": []
        },
        {
            "name": "No Match",
            "price": 25.99,
            "is_vegetarian": False,
            "is_gluten_free": False,
            "allergen_ids": [allergen_id]
        }
    ]
    
    for item in items:
        client.post(
            "/api/menu/items/",
            json={
                **item,
                "category_id": sample_category.id
            }
        )
    
    # Test combined filters
    response = client.get(
        "/api/menu/menu-items/filter?"
        "min_price=10&max_price=20"
        "&is_vegetarian=true"
        "&is_gluten_free=true"
        f"&allergen_exclude_ids={allergen_id}"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Perfect Match"

def test_get_menu(client, sample_category, sample_menu_item):
    """Test getting the complete menu with categories and items"""
    response = client.get("/api/menu")
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure
    assert "categories" in data
    assert isinstance(data["categories"], list)
    assert len(data["categories"]) > 0
    
    # Verify category structure
    category = data["categories"][0]
    assert "id" in category
    assert "name" in category
    assert "menu_items" in category
    assert isinstance(category["menu_items"], list)
    
    # Verify menu item structure
    if len(category["menu_items"]) > 0:
        menu_item = category["menu_items"][0]
        assert "id" in menu_item
        assert "name" in menu_item
        assert "price" in menu_item
        assert "category" in menu_item
        assert isinstance(menu_item["category"], str)
        assert menu_item["category"] == sample_category.name
