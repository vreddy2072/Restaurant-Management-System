from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

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
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ShoppingCartBase(BaseModel):
    user_id: int

class ShoppingCartCreate(ShoppingCartBase):
    pass

class ShoppingCart(ShoppingCartBase):
    id: int
    items: List[CartItem]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CartResponse(BaseModel):
    id: Optional[int] = None
    user_id: Optional[int] = None
    items: List[CartItem] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
