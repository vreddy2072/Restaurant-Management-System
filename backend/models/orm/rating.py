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
    service_rating = Column(Integer, nullable=False)
    ambiance_rating = Column(Integer, nullable=False)
    cleanliness_rating = Column(Integer, nullable=False)
    value_rating = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint('service_rating >= 1 AND service_rating <= 5', name='check_service_rating_range'),
        CheckConstraint('ambiance_rating >= 1 AND ambiance_rating <= 5', name='check_ambiance_rating_range'),
        CheckConstraint('cleanliness_rating >= 1 AND cleanliness_rating <= 5', name='check_cleanliness_rating_range'),
        CheckConstraint('value_rating >= 1 AND value_rating <= 5', name='check_value_rating_range'),
    )

    # Use string references to avoid circular imports
    user = relationship("User", back_populates="restaurant_feedback")

    def __init__(self, **kwargs):
        for rating_field in ['service_rating', 'ambiance_rating', 'cleanliness_rating', 'value_rating']:
            if rating_field in kwargs and (kwargs[rating_field] < 1 or kwargs[rating_field] > 5):
                raise ValueError(f"{rating_field.replace('_', ' ').title()} must be between 1 and 5")
        if 'feedback_text' in kwargs and len(kwargs['feedback_text'].strip()) == 0:
            raise ValueError("Feedback text cannot be empty")
        super().__init__(**kwargs)

    def to_dict(self):
        """Convert feedback to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "feedback_text": self.feedback_text,
            "service_rating": self.service_rating,
            "ambiance_rating": self.ambiance_rating,
            "cleanliness_rating": self.cleanliness_rating,
            "value_rating": self.value_rating,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
