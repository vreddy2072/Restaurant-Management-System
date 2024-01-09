from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
import re

from backend.utils.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    role = Column(String(20), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    is_guest = Column(Boolean, nullable=False, default=False)
    is_admin = Column(Boolean, nullable=False, default=False)
    phone_number = Column(String(20), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Use string references to avoid circular imports
    shopping_cart = relationship("ShoppingCart", back_populates="user", uselist=False)
    menu_item_ratings = relationship("MenuItemRating", back_populates="user")
    restaurant_feedback = relationship("RestaurantFeedback", back_populates="user")

    VALID_ROLES = ["admin", "staff", "customer"]
    EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

    def __init__(self, **kwargs):
        # Validate role
        if "role" in kwargs and kwargs["role"] not in self.VALID_ROLES:
            raise ValueError(f"Invalid role. Must be one of: {', '.join(self.VALID_ROLES)}")
        
        # Validate email
        if "email" in kwargs and not self.EMAIL_REGEX.match(kwargs["email"]):
            raise ValueError("Invalid email address")

        super().__init__(**kwargs)

    def __repr__(self):
        return f"<User {self.username}>"

    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "role": self.role,
            "is_active": self.is_active,
            "is_guest": self.is_guest,
            "is_admin": self.is_admin,
            "phone_number": self.phone_number,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
