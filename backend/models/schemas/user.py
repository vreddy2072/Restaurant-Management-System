from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, constr

# Shared properties
class UserBase(BaseModel):
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    role: constr(pattern='^(admin|staff|customer)$')
    phone_number: Optional[str] = None

# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str

# Properties to receive via API on update
class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    password: Optional[str] = None
    email: Optional[EmailStr] = None

# Properties to return via API
class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Properties to receive via API on login
class UserLogin(BaseModel):
    email: EmailStr
    password: str
