from typing import Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime

class MenuItemRatingBase(BaseModel):
    menu_item_id: int
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None

    @validator('comment')
    def comment_not_empty(cls, v):
        if v is not None and len(v.strip()) == 0:
            raise ValueError('Comment cannot be empty string')
        return v

class MenuItemRatingCreate(MenuItemRatingBase):
    pass

class MenuItemRating(MenuItemRatingBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class MenuItemRatingResponse(MenuItemRating):
    pass

class RestaurantFeedbackBase(BaseModel):
    feedback_text: str = Field(..., min_length=1, max_length=1000)
    service_rating: int = Field(..., ge=1, le=5)
    ambiance_rating: int = Field(..., ge=1, le=5)
    cleanliness_rating: int = Field(..., ge=1, le=5)
    value_rating: int = Field(..., ge=1, le=5)

    @validator('feedback_text')
    def feedback_not_empty(cls, v):
        if len(v.strip()) == 0:
            raise ValueError('Feedback text cannot be empty')
        return v

class RestaurantFeedbackCreate(RestaurantFeedbackBase):
    pass

class RestaurantFeedback(RestaurantFeedbackBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class RestaurantFeedbackResponse(RestaurantFeedback):
    pass

class RestaurantFeedbackStats(BaseModel):
    """Statistics for restaurant feedback"""
    average_service_rating: float = Field(..., ge=0, le=5)
    average_ambiance_rating: float = Field(..., ge=0, le=5)
    average_cleanliness_rating: float = Field(..., ge=0, le=5)
    average_value_rating: float = Field(..., ge=0, le=5)
    total_reviews: int = Field(..., ge=0)
