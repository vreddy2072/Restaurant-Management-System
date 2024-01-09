from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from backend.models.orm.menu import Category, MenuItem, Allergen
from backend.models.schemas.menu import (
    CategoryCreate, CategoryUpdate,
    MenuItemCreate, MenuItemUpdate,
    AllergenCreate, AllergenUpdate,
    MenuItemFilters
)
from backend.services.menu_service import MenuService
from fastapi import HTTPException, status

# Allergen CRUD operations
def create_allergen(db: Session, allergen: AllergenCreate) -> Allergen:
    db_allergen = Allergen(**allergen.model_dump())
    db.add(db_allergen)
    db.commit()
    db.refresh(db_allergen)
    return db_allergen

def get_allergen(db: Session, allergen_id: int) -> Optional[Allergen]:
    return db.query(Allergen).filter(Allergen.id == allergen_id).first()

def get_allergens(db: Session, skip: int = 0, limit: int = 100) -> List[Allergen]:
    return db.query(Allergen).offset(skip).limit(limit).all()

def update_allergen(db: Session, allergen_id: int, allergen: AllergenUpdate) -> Optional[Allergen]:
    db_allergen = get_allergen(db, allergen_id)
    if db_allergen:
        update_data = allergen.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_allergen, key, value)
        db.commit()
        db.refresh(db_allergen)
    return db_allergen

def delete_allergen(db: Session, allergen_id: int) -> bool:
    db_allergen = get_allergen(db, allergen_id)
    if db_allergen:
        db.delete(db_allergen)
        db.commit()
        return True
    return False

# Enhanced MenuItem operations
def create_menu_item(db: Session, menu_item: MenuItemCreate) -> MenuItem:
    menu_item_data = menu_item.model_dump(exclude={'allergen_ids'})
    db_menu_item = MenuItem(**menu_item_data)
    
    if menu_item.allergen_ids:
        allergens = db.query(Allergen).filter(Allergen.id.in_(menu_item.allergen_ids)).all()
        db_menu_item.allergens = allergens
    
    db.add(db_menu_item)
    db.commit()
    db.refresh(db_menu_item)
    return db_menu_item

def get_menu_item(db: Session, item_id: int) -> MenuItem:
    menu_item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not menu_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Menu item with id {item_id} not found"
        )
    return menu_item

def update_menu_item(db: Session, menu_item_id: int, menu_item: MenuItemUpdate) -> Optional[MenuItem]:
    db_menu_item = get_menu_item(db, menu_item_id)
    if db_menu_item:
        update_data = menu_item.model_dump(exclude_unset=True, exclude={'allergen_ids'})
        for key, value in update_data.items():
            setattr(db_menu_item, key, value)
        
        if menu_item.allergen_ids is not None:
            allergens = db.query(Allergen).filter(Allergen.id.in_(menu_item.allergen_ids)).all()
            db_menu_item.allergens = allergens
        
        db.commit()
        db.refresh(db_menu_item)
    return db_menu_item

def get_filtered_menu_items(
    db: Session,
    filters: MenuItemFilters,
    skip: int = 0,
    limit: int = 100
) -> List[MenuItem]:
    query = db.query(MenuItem)
    
    # Apply filters
    if filters.category_id is not None:
        query = query.filter(MenuItem.category_id == filters.category_id)
    if filters.is_vegetarian is not None:
        query = query.filter(MenuItem.is_vegetarian == filters.is_vegetarian)
    if filters.is_vegan is not None:
        query = query.filter(MenuItem.is_vegan == filters.is_vegan)
    if filters.is_gluten_free is not None:
        query = query.filter(MenuItem.is_gluten_free == filters.is_gluten_free)
    if filters.min_price is not None:
        query = query.filter(MenuItem.price >= filters.min_price)
    if filters.max_price is not None:
        query = query.filter(MenuItem.price <= filters.max_price)
    if filters.min_rating is not None:
        query = query.filter(MenuItem.average_rating >= filters.min_rating)
    if filters.allergen_exclude_ids:
        # Exclude items that have any of the specified allergens
        query = query.filter(~MenuItem.allergens.any(Allergen.id.in_(filters.allergen_exclude_ids)))
    
    return query.offset(skip).limit(limit).all()

# Keep existing Category CRUD operations... 