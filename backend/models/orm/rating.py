from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.utils.database import Base

class MenuItemRating(Base):
    __tablename__ = "menu_item_ratings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False, index=True)
    rating = Column(Integer, nullable=False)
    comment = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range'),
        UniqueConstraint('user_id', 'menu_item_id', name='uq_user_menu_item_rating'),
    )

    # Use string references to avoid circular imports
    user = relationship("User", back_populates="menu_item_ratings")
    menu_item = relationship("MenuItem", back_populates="ratings")

    def __init__(self, **kwargs):
        if 'rating' in kwargs and (kwargs['rating'] < 1 or kwargs['rating'] > 5):
            raise ValueError("Rating must be between 1 and 5")
        super().__init__(**kwargs)

class RestaurantFeedback(Base):
    __tablename__ = "restaurant_feedback"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    feedback_text = Column(String(1000), nullable=False)
    category = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    VALID_CATEGORIES = ["service", "food", "ambiance", "cleanliness", "other"]

    # Use string references to avoid circular imports
    user = relationship("User", back_populates="restaurant_feedback")

    def __init__(self, **kwargs):
        if 'category' in kwargs and kwargs['category'] not in self.VALID_CATEGORIES:
            raise ValueError(f"Invalid category. Must be one of: {', '.join(self.VALID_CATEGORIES)}")
        if 'feedback_text' in kwargs and len(kwargs['feedback_text'].strip()) == 0:
            raise ValueError("Feedback text cannot be empty")
        super().__init__(**kwargs)
