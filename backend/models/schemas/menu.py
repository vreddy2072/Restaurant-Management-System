from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

from .base import TimestampedModel

class AllergenBase(BaseModel):
    name: str
    description: Optional[str] = None

class AllergenCreate(AllergenBase):
    pass

class AllergenUpdate(AllergenBase):
    name: Optional[str] = None

class Allergen(AllergenBase, TimestampedModel):
    id: int

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    name: Optional[str] = None
    is_active: Optional[bool] = None

class MenuItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category_id: int
    is_vegetarian: Optional[bool] = False
    is_vegan: Optional[bool] = False
    is_gluten_free: Optional[bool] = False
    spice_level: Optional[int] = Field(0, ge=0, le=3)
    preparation_time: Optional[int] = None
    customization_options: Optional[Dict[str, List[str]]] = Field(default_factory=dict)
    image_url: Optional[str] = None

class MenuItemCreate(MenuItemBase):
    allergen_ids: Optional[List[int]] = None

class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category_id: Optional[int] = None
    is_vegetarian: Optional[bool] = None
    is_vegan: Optional[bool] = None
    is_gluten_free: Optional[bool] = None
    spice_level: Optional[int] = None
    preparation_time: Optional[int] = None
    is_active: Optional[bool] = None
    customization_options: Optional[Dict[str, List[str]]] = None
    allergen_ids: Optional[List[int]] = None
    average_rating: Optional[float] = None
    rating_count: Optional[int] = None
    image_url: Optional[str] = None

class MenuItem(MenuItemBase, TimestampedModel):
    id: int
    is_active: bool
    category: Optional[str] = None
    average_rating: float = 0.0
    rating_count: int = 0
    allergens: List[Allergen] = []
    selected_customization: Optional[Dict[str, str]] = None

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, obj):
        # Create a dict with only the fields we want
        obj_dict = {
            'id': obj.id,
            'name': obj.name,
            'description': obj.description,
            'price': obj.price,
            'category_id': obj.category_id,
            'is_vegetarian': obj.is_vegetarian,
            'is_vegan': obj.is_vegan,
            'is_gluten_free': obj.is_gluten_free,
            'spice_level': obj.spice_level,
            'preparation_time': obj.preparation_time,
            'customization_options': obj.customization_options,
            'image_url': obj.image_url,
            'is_active': obj.is_active,
            'created_at': obj.created_at,
            'updated_at': obj.updated_at,
            'average_rating': obj.average_rating,
            'rating_count': obj.rating_count,
            'allergens': obj.allergens,
            'category': obj.category.name if obj.category else None,
            'selected_customization': obj.selected_customization
        }
        return cls(**obj_dict)

class Category(CategoryBase, TimestampedModel):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

class CategoryWithItems(Category):
    menu_items: List[MenuItem] = []

    class Config:
        from_attributes = True

class MenuResponse(BaseModel):
    categories: List[CategoryWithItems]

class MenuItemFilters(BaseModel):
    category_id: Optional[int] = None
    is_vegetarian: Optional[bool] = None
    is_vegan: Optional[bool] = None
    is_gluten_free: Optional[bool] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_rating: Optional[float] = Field(None, ge=0, le=5)
    allergen_exclude_ids: Optional[List[int]] = None

class RatingCreate(BaseModel):
    """Schema for creating a rating"""
    rating: float = Field(..., ge=0, le=5, description="Rating value between 0 and 5")