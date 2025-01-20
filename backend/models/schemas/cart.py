from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

class MenuItemInCart(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    image_url: Optional[str] = None
    customization_options: Optional[Dict[str, List[str]]] = None

    class Config:
        from_attributes = True

class CartItemBase(BaseModel):
    menu_item_id: int
    quantity: int
    customizations: Optional[Dict[str, Any]] = None

class CartItemCreate(CartItemBase):
    pass

class CartItemUpdate(BaseModel):
    quantity: Optional[int] = None
    customizations: Optional[Dict[str, Any]] = None

class CartItem(CartItemBase):
    id: int
    cart_id: int
    menu_item: MenuItemInCart
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ShoppingCartBase(BaseModel):
    user_id: int
    order_number: Optional[str] = None

class ShoppingCartCreate(ShoppingCartBase):
    pass

class ShoppingCartUpdate(BaseModel):
    order_number: Optional[str] = None

class ShoppingCart(ShoppingCartBase):
    id: int
    cart_items: List[CartItem]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CartResponse(BaseModel):
    id: Optional[int] = None
    user_id: Optional[int] = None
    order_number: Optional[str] = None
    cart_items: List[CartItem] = []
    created_at: datetime

    class Config:
        from_attributes = True
