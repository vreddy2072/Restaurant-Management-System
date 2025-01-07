from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, constr, field_validator
import re

# Custom email validator
def validate_email(email: str) -> str:
    email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z.]{2,}$')
    if not email_regex.match(email):
        raise ValueError('Invalid email format')
    return email

# Shared properties
class UserBase(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    role: constr(pattern='^(admin|staff|customer)$')
    phone_number: Optional[str] = None

    @field_validator('email')
    def validate_email_format(cls, v):
        return validate_email(v)

# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str

# Properties to receive via API on update
class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    password: Optional[str] = None
    email: Optional[str] = None

    @field_validator('email')
    def validate_email_format(cls, v):
        if v is None:
            return v
        return validate_email(v)

# Properties to return via API
class UserResponse(UserBase):
    id: int
    is_active: bool
    is_guest: bool
    is_admin: bool  # Added this field to match frontend interface
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Properties to receive via API on login
class UserLogin(BaseModel):
    email: str
    password: str

    @field_validator('email')
    def validate_email_format(cls, v):
        return validate_email(v)
