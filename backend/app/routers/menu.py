from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas
from ..database import get_db
from .. import models

router = APIRouter()

@router.patch("/items/{item_id}", response_model=schemas.MenuItem)
def update_menu_item(
    item_id: int,
    item: schemas.MenuItemUpdate,
    db: Session = Depends(get_db)
):
    updated_item = crud.update_menu_item(db, item_id, item)
    if updated_item is None:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return updated_item 

@router.get("/items/{item_id}/debug", response_model=None)
def get_menu_item_debug(item_id: int, db: Session = Depends(get_db)):
    """Debug endpoint to get raw menu item data"""
    item = db.query(models.MenuItem).filter(models.MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    
    # Get raw database values
    raw_data = {
        'id': item.id,
        'name': item.name,
        'allergens': item.allergens,
        'allergens_type': str(type(item.allergens)),
        '_sa_instance_state': str(item.__dict__.get('_sa_instance_state')),
        'raw_dict': str(item.__dict__)
    }
    return raw_data 

@router.get("/allergens", response_model=List[schemas.AllergenBase])
def get_allergens(db: Session = Depends(get_db)):
    """Get all available allergens"""
    return [
        {"id": 1, "name": "Dairy", "description": "Milk and dairy products"},
        {"id": 2, "name": "Eggs", "description": "Eggs and egg products"},
        {"id": 3, "name": "Fish", "description": "Fish and fish products"},
        {"id": 4, "name": "Shellfish", "description": "Shellfish and products"},
        {"id": 5, "name": "Tree Nuts", "description": "Tree nuts and products"},
        {"id": 6, "name": "Peanuts", "description": "Peanuts and products"},
        {"id": 7, "name": "Wheat", "description": "Wheat and products"},
        {"id": 8, "name": "Soy", "description": "Soy and products"},
        {"id": 9, "name": "Sesame", "description": "Sesame and products"}
    ] 