from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, func
from sqlalchemy.orm import relationship

from backend.utils.database import Base

class ShoppingCart(Base):
    __tablename__ = "shopping_carts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    order_number = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="shopping_carts")
    cart_items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ShoppingCart user_id={self.user_id}>"

    def to_dict(self):
        """Convert shopping cart to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "order_number": self.order_number,
            "items": [item.to_dict() for item in self.cart_items],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True)
    cart_id = Column(Integer, ForeignKey("shopping_carts.id"), nullable=False, index=True)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False, default=1)
    customizations = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    cart = relationship("ShoppingCart", back_populates="cart_items")
    menu_item = relationship("MenuItem")

    def __repr__(self):
        return f"<CartItem id={self.id} cart_id={self.cart_id} menu_item_id={self.menu_item_id}>"

    def to_dict(self):
        """Convert cart item to dictionary"""
        return {
            "id": self.id,
            "cart_id": self.cart_id,
            "menu_item_id": self.menu_item_id,
            "menu_item": self.menu_item.to_dict() if self.menu_item else None,
            "quantity": self.quantity,
            "customizations": self.customizations,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
