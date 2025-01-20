from typing import Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

class OrderStatus(str, Enum):
    INITIALIZED = "initialized"
    IN_PROGRESS = "in_progress"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class OrderBase(BaseModel):
    """Base schema for order data"""
    customer_name: str = Field(..., min_length=1, max_length=100)
    is_group_order: bool = Field(default=False)

class OrderCreate(OrderBase):
    """Schema for creating a new order"""
    pass

class OrderUpdate(BaseModel):
    """Schema for updating an order"""
    status: Optional[OrderStatus] = None

class OrderResponse(OrderBase):
    """Schema for order response"""
    id: int
    order_number: str
    table_number: int
    user_id: int
    status: OrderStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True 