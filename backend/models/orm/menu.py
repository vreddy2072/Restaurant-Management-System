from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Table, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import DateTime

from backend.utils.database import Base
from backend.models.orm.rating import MenuItemRating

# Junction table for menu items and allergens
menu_item_allergens = Table(
    'menu_item_allergens',
    Base.metadata,
    Column('menu_item_id', Integer, ForeignKey('menu_items.id'), primary_key=True),
    Column('allergen_id', Integer, ForeignKey('allergens.id'), primary_key=True)
)

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    menu_items = relationship("MenuItem", back_populates="category")

class Allergen(Base):
    __tablename__ = "allergens"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    menu_items = relationship("MenuItem", secondary=menu_item_allergens, back_populates="allergens")

class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    price = Column(Float)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    is_vegetarian = Column(Boolean, default=False)
    is_vegan = Column(Boolean, default=False)
    is_gluten_free = Column(Boolean, default=False)
    spice_level = Column(Integer, default=0)
    preparation_time = Column(Integer, nullable=True)  # in minutes
    is_active = Column(Boolean, default=True)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    customization_options = Column(JSON, default=dict)
    average_rating = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)
    image_url = Column(String, nullable=True)

    category = relationship("Category", back_populates="menu_items")
    allergens = relationship("Allergen", secondary=menu_item_allergens, back_populates="menu_items")
    ratings = relationship("MenuItemRating", back_populates="menu_item", cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        if 'price' in kwargs and kwargs['price'] < 0:
            raise ValueError("Price cannot be negative")
        super().__init__(**kwargs)

    def to_dict(self):
        """Convert the menu item to a dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "category_id": self.category_id,
            "is_vegetarian": self.is_vegetarian,
            "is_vegan": self.is_vegan,
            "is_gluten_free": self.is_gluten_free,
            "spice_level": self.spice_level,
            "preparation_time": self.preparation_time,
            "is_active": self.is_active,
            "is_available": self.is_available,
            "customization_options": self.customization_options,
            "average_rating": self.average_rating,
            "rating_count": self.rating_count,
            "image_url": self.image_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }