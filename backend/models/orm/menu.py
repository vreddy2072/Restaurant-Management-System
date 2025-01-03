from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Table, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import DateTime

from backend.utils.database import Base

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
    category_id = Column(Integer, ForeignKey("categories.id"))
    is_vegetarian = Column(Boolean, default=False)
    is_vegan = Column(Boolean, default=False)
    is_gluten_free = Column(Boolean, default=False)
    spice_level = Column(Integer, default=0)
    preparation_time = Column(Integer, nullable=True)  # in minutes
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    customization_options = Column(JSON, default=dict)
    average_rating = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)
    image_url = Column(String, nullable=True)

    category = relationship("Category", back_populates="menu_items")
    allergens = relationship("Allergen", secondary=menu_item_allergens, back_populates="menu_items") 