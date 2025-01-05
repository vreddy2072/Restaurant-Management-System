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
    category: str

    @validator('category')
    def validate_category(cls, v):
        valid_categories = ["service", "food", "ambiance", "cleanliness", "other"]
        if v not in valid_categories:
            raise ValueError(f"Category must be one of: {', '.join(valid_categories)}")
        return v

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
