from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime

class AllergenBase(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

class MenuItemBase(BaseModel):
    name: str
    description: str
    price: float
    category_id: int
    is_active: bool = True
    is_vegetarian: bool = False
    is_vegan: bool = False
    is_gluten_free: bool = False
    spice_level: int = 0
    preparation_time: int = 15
    allergens: List[AllergenBase] = []
    customization_options: Dict[str, List[str]] = {}

class MenuItemCreate(MenuItemBase):
    pass

class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category_id: Optional[int] = None
    is_active: Optional[bool] = None
    is_vegetarian: Optional[bool] = None
    is_vegan: Optional[bool] = None
    is_gluten_free: Optional[bool] = None
    spice_level: Optional[int] = None
    preparation_time: Optional[int] = None
    allergens: Optional[List[AllergenBase]] = None
    customization_options: Optional[Dict[str, List[str]]] = None

class MenuItem(MenuItemBase):
    id: int
    image_url: Optional[str] = None
    average_rating: float = 0
    rating_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True 