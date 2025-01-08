from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import os
import shutil
from pathlib import Path
import logging

from backend.models.schemas.menu import (
    Category, CategoryCreate, CategoryUpdate,
    MenuItem, MenuItemCreate, MenuItemUpdate,
    Allergen, AllergenCreate, AllergenUpdate,
    MenuResponse, CategoryWithItems, MenuItemFilters,
    RatingCreate
)
from backend.services.menu_service import MenuService
from backend.utils.database import get_db

router = APIRouter(prefix="/api/menu", tags=["menu"])

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create images directory if it doesn't exist
IMAGES_DIR = Path("static/images")
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# Category routes
@router.post("/categories/", response_model=Category, status_code=201)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """Create a new menu category"""
    return MenuService.create_category(db, category)

@router.get("/categories/", response_model=List[Category])
def get_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    active_only: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Get all menu categories"""
    return MenuService.get_categories(db, skip, limit, active_only)

@router.get("/categories/{category_id}", response_model=Category)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """Get a specific menu category by ID"""
    category = MenuService.get_category(db, category_id)
    if not category.is_active:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.api_route("/categories/{category_id}", methods=["PUT", "PATCH"], response_model=Category)
def update_category(
    category_id: int,
    category: CategoryUpdate,
    db: Session = Depends(get_db)
):
    """Update a menu category"""
    return MenuService.update_category(db, category_id, category)

@router.delete("/categories/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    """Soft delete a menu category"""
    MenuService.delete_category(db, category_id)
    return {"message": "Category deleted successfully"}

# Menu item routes
@router.post("/items/", response_model=MenuItem, status_code=201)
def create_menu_item(menu_item: MenuItemCreate, db: Session = Depends(get_db)):
    """Create a new menu item"""
    try:
        return MenuService.create_menu_item(db, menu_item)
    except HTTPException as e:
        if e.status_code == 404:
            raise HTTPException(
                status_code=400,
                detail=f"Category with id {menu_item.category_id} not found"
            )
        raise e

@router.get("/items/", response_model=List[MenuItem])
def get_menu_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    category_id: Optional[int] = None,
    active_only: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Get all menu items, optionally filtered by category"""
    logger.info(f"Fetching menu items with params: skip={skip}, limit={limit}, category_id={category_id}, active_only={active_only}")
    items = MenuService.get_menu_items(db, skip, limit, category_id, active_only)
    logger.info(f"Found {len(items)} menu items")
    return items

@router.get("/items/filter", response_model=List[MenuItem])
def filter_menu_items(
    is_vegetarian: Optional[bool] = None,
    is_vegan: Optional[bool] = None,
    is_gluten_free: Optional[bool] = None,
    allergen_exclude_ids: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Filter menu items by dietary preferences and allergens"""
    allergen_ids = []
    if allergen_exclude_ids:
        allergen_ids = [int(id) for id in allergen_exclude_ids.split(",")]
    
    return MenuService.filter_menu_items(
        db,
        is_vegetarian=is_vegetarian,
        is_vegan=is_vegan,
        is_gluten_free=is_gluten_free,
        allergen_exclude_ids=allergen_ids
    )

@router.get("/items/{item_id}", response_model=MenuItem)
def get_menu_item(item_id: int, db: Session = Depends(get_db)):
    """Get a specific menu item by ID"""
    item = MenuService.get_menu_item(db, item_id)
    if not item.is_active:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return item

@router.api_route("/items/{item_id}", methods=["PUT", "PATCH"], response_model=MenuItem)
def update_menu_item(
    item_id: int,
    menu_item: MenuItemUpdate,
    db: Session = Depends(get_db)
):
    """Update a menu item"""
    return MenuService.update_menu_item(db, item_id, menu_item)

@router.delete("/items/{item_id}")
def delete_menu_item(item_id: int, db: Session = Depends(get_db)):
    """Soft delete a menu item"""
    MenuService.delete_menu_item(db, item_id)
    return {"message": "Menu item deleted successfully"}

@router.post("/items/{item_id}/rate")
def rate_menu_item(
    item_id: int,
    rating_data: RatingCreate,
    db: Session = Depends(get_db)
):
    """Rate a menu item"""
    item = MenuService.get_menu_item(db, item_id)
    if not item.is_active:
        raise HTTPException(status_code=404, detail="Menu item not found")
    
    # Update rating
    if item.rating_count is None:
        item.rating_count = 0
        item.average_rating = 0
    
    item.rating_count += 1
    item.average_rating = ((item.average_rating * (item.rating_count - 1)) + rating_data.rating) / item.rating_count
    db.commit()
    db.refresh(item)
    
    return {
        "id": item.id,
        "average_rating": item.average_rating,
        "rating_count": item.rating_count
    }

@router.post("/items/{item_id}/customize", response_model=MenuItem)
def customize_menu_item(
    item_id: int,
    customization: dict,
    db: Session = Depends(get_db)
):
    """Customize a menu item with selected options"""
    item = MenuService.get_menu_item(db, item_id)
    if not item.is_active:
        raise HTTPException(status_code=404, detail="Menu item not found")
    
    # Validate customization options
    if not item.customization_options:
        raise HTTPException(
            status_code=400,
            detail="This item does not support customization"
        )
    
    # Validate each customization option
    for option, value in customization.items():
        if option not in item.customization_options:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid customization option: {option}"
            )
        
        valid_values = item.customization_options[option]
        if isinstance(value, list):
            for v in value:
                if v not in valid_values:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid value '{v}' for option '{option}'"
                    )
        else:
            if value not in valid_values:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid value '{value}' for option '{option}'"
                )
    
    # Store customization with the menu item
    item.selected_customization = customization
    db.commit()
    db.refresh(item)
    
    # Return the item with the category name as a string
    return MenuItem.from_orm(item)

@router.get("/full", response_model=List[CategoryWithItems])
def get_full_menu(
    active_only: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Get the full menu with categories and items"""
    logger.info(f"Fetching full menu with active_only={active_only}")
    categories = MenuService.get_categories(db, active_only=active_only)
    logger.info(f"Found {len(categories)} categories")
    menu_items = MenuService.get_menu_items(db, active_only=active_only)
    logger.info(f"Found {len(menu_items)} menu items")
    
    # Group menu items by category
    menu_by_category = []
    for category in categories:
        category_items = [item for item in menu_items if item.category_id == category.id]
        menu_by_category.append(CategoryWithItems(
            **category.__dict__,
            menu_items=category_items
        ))
    
    logger.info(f"Returning menu with {len(menu_by_category)} categories")
    return menu_by_category

@router.post("/items/{item_id}/image")
async def upload_menu_item_image(
    item_id: int,
    file: UploadFile,
    db: Session = Depends(get_db)
):
    """Upload an image for a menu item"""
    item = MenuService.get_menu_item(db, item_id)
    if not item.is_active:
        raise HTTPException(status_code=404, detail="Menu item not found")
    
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="File must be an image"
        )
    
    # Create unique filename
    file_extension = os.path.splitext(file.filename)[1]
    filename = f"menu_item_{item_id}{file_extension}"
    file_path = IMAGES_DIR / filename
    
    # Save file
    try:
        contents = await file.read()
        with file_path.open("wb") as buffer:
            buffer.write(contents)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Could not upload image"
        )
    
    # Update menu item with image URL
    item.image_url = f"/static/images/{filename}"
    db.commit()
    db.refresh(item)
    
    return {"image_url": item.image_url}

# Allergen endpoints
@router.post("/allergens/", response_model=Allergen, status_code=201)
def create_allergen(
    allergen: AllergenCreate,
    db: Session = Depends(get_db)
):
    return MenuService.create_allergen(db=db, allergen=allergen)

@router.get("/allergens/", response_model=List[Allergen])
def read_allergens(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return MenuService.get_allergens(db, skip=skip, limit=limit)

@router.get("/allergens/{allergen_id}", response_model=Allergen)
def read_allergen(
    allergen_id: int,
    db: Session = Depends(get_db)
):
    db_allergen = MenuService.get_allergen(db, allergen_id=allergen_id)
    if db_allergen is None:
        raise HTTPException(status_code=404, detail="Allergen not found")
    return db_allergen

@router.api_route("/allergens/{allergen_id}", methods=["PUT", "PATCH"], response_model=Allergen)
def update_allergen(
    allergen_id: int,
    allergen: AllergenUpdate,
    db: Session = Depends(get_db)
):
    db_allergen = MenuService.update_allergen(db, allergen_id=allergen_id, allergen=allergen)
    if db_allergen is None:
        raise HTTPException(status_code=404, detail="Allergen not found")
    return db_allergen

@router.delete("/allergens/{allergen_id}")
def delete_allergen(
    allergen_id: int,
    db: Session = Depends(get_db)
):
    success = MenuService.delete_allergen(db, allergen_id=allergen_id)
    if not success:
        raise HTTPException(status_code=404, detail="Allergen not found")
    return {"detail": "Allergen deleted successfully"}

# Enhanced menu item endpoints
@router.get("/menu-items/filter", response_model=List[MenuItem])
def filter_menu_items(
    category_id: int = Query(None, description="Filter by category ID"),
    is_vegetarian: bool = Query(None, description="Filter vegetarian items"),
    is_vegan: bool = Query(None, description="Filter vegan items"),
    is_gluten_free: bool = Query(None, description="Filter gluten-free items"),
    min_price: float = Query(None, description="Minimum price"),
    max_price: float = Query(None, description="Maximum price"),
    min_rating: float = Query(None, ge=0, le=5, description="Minimum rating"),
    allergen_exclude_ids: List[int] = Query(None, description="IDs of allergens to exclude"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    filters = MenuItemFilters(
        category_id=category_id,
        is_vegetarian=is_vegetarian,
        is_vegan=is_vegan,
        is_gluten_free=is_gluten_free,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
        allergen_exclude_ids=allergen_exclude_ids
    )
    return MenuService.get_filtered_menu_items(db=db, filters=filters, skip=skip, limit=limit)

# Keep existing category and menu item endpoints, but update create/update menu item to include allergens
@router.post("/menu-items/", response_model=MenuItem, status_code=201)
def create_menu_item(
    menu_item: MenuItemCreate,
    db: Session = Depends(get_db)
):
    return MenuService.create_menu_item(db=db, menu_item=menu_item)

@router.put("/menu-items/{menu_item_id}", response_model=MenuItem)
def update_menu_item(
    menu_item_id: int,
    menu_item: MenuItemUpdate,
    db: Session = Depends(get_db)
):
    db_menu_item = MenuService.update_menu_item(
        db, menu_item_id=menu_item_id, menu_item=menu_item
    )
    if db_menu_item is None:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return db_menu_item

# Full menu route
@router.get("/", response_model=MenuResponse)
def get_menu(
    active_only: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Get the complete menu structure"""
    categories = MenuService.get_categories(db, active_only=active_only)
    menu_items = MenuService.get_menu_items(db, active_only=active_only)
    
    # Group menu items by category
    categories_with_items = []
    for category in categories:
        category_items = [
            {
                **item.__dict__,
                "category": category.name  # Add category name as string
            }
            for item in menu_items 
            if item.category_id == category.id
        ]
        categories_with_items.append({
            **category.__dict__,
            "menu_items": category_items
        })
    
    return {"categories": categories_with_items}

@router.post("/items/{item_id}/image", response_model=MenuItem)
async def upload_menu_item_image(
    item_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload an image for a menu item"""
    # Verify menu item exists
    menu_item = MenuService.get_menu_item(db, item_id)
    
    # Verify file is an image
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="File must be an image"
        )
    
    # Create a unique filename
    file_extension = file.filename.split(".")[-1]
    filename = f"menu_item_{item_id}.{file_extension}"
    file_path = IMAGES_DIR / filename
    
    # Save the file
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Could not upload image: {str(e)}"
        )
    finally:
        file.file.close()
    
    # Update menu item with image URL
    image_url = f"/static/images/{filename}"
    return MenuService.update_menu_item(
        db,
        item_id,
        MenuItemUpdate(image_url=image_url)
    ) 