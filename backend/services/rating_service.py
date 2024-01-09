from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from backend.models.orm.rating import MenuItemRating, RestaurantFeedback
from backend.models.schemas.rating import MenuItemRatingCreate, RestaurantFeedbackCreate

class RatingService:
    def __init__(self, db: Session):
        self.db = db

    def create_menu_item_rating(self, rating: MenuItemRatingCreate, user_id: int) -> MenuItemRating:
        """Create a new rating for a menu item."""
        try:
            db_rating = MenuItemRating(
                user_id=user_id,
                menu_item_id=rating.menu_item_id,
                rating=rating.rating,
                comment=rating.comment
            )
            self.db.add(db_rating)
            self.db.commit()
            self.db.refresh(db_rating)
            return db_rating
        except IntegrityError:
            self.db.rollback()
            raise ValueError("User has already rated this menu item")

    def get_menu_item_ratings(self, menu_item_id: int) -> List[MenuItemRating]:
        """Get all ratings for a specific menu item."""
        return self.db.query(MenuItemRating).filter(MenuItemRating.menu_item_id == menu_item_id).all()

    def get_user_menu_item_rating(self, user_id: int, menu_item_id: int) -> Optional[MenuItemRating]:
        """Get a user's rating for a specific menu item."""
        return self.db.query(MenuItemRating).filter(
            MenuItemRating.user_id == user_id,
            MenuItemRating.menu_item_id == menu_item_id
        ).first()

    def update_menu_item_rating(self, user_id: int, menu_item_id: int, rating: MenuItemRatingCreate) -> MenuItemRating:
        """Update a user's rating for a menu item."""
        db_rating = self.get_user_menu_item_rating(user_id, menu_item_id)
        if not db_rating:
            raise ValueError("Rating not found")

        db_rating.rating = rating.rating
        db_rating.comment = rating.comment
        self.db.commit()
        self.db.refresh(db_rating)
        return db_rating

    def delete_menu_item_rating(self, user_id: int, menu_item_id: int) -> bool:
        """Delete a user's rating for a menu item."""
        db_rating = self.get_user_menu_item_rating(user_id, menu_item_id)
        if not db_rating:
            return False

        self.db.delete(db_rating)
        self.db.commit()
        return True

    def create_restaurant_feedback(self, feedback: RestaurantFeedbackCreate, user_id: int) -> RestaurantFeedback:
        """Create new restaurant feedback."""
        db_feedback = RestaurantFeedback(
            user_id=user_id,
            feedback_text=feedback.feedback_text,
            category=feedback.category
        )
        self.db.add(db_feedback)
        self.db.commit()
        self.db.refresh(db_feedback)
        return db_feedback

    def get_restaurant_feedback(self, category: Optional[str] = None) -> List[RestaurantFeedback]:
        """Get all restaurant feedback, optionally filtered by category."""
        query = self.db.query(RestaurantFeedback)
        if category:
            if category not in RestaurantFeedback.VALID_CATEGORIES:
                raise ValueError(f"Invalid category. Must be one of: {', '.join(RestaurantFeedback.VALID_CATEGORIES)}")
            query = query.filter(RestaurantFeedback.category == category)
        return query.all()

    def get_user_feedback(self, user_id: int) -> List[RestaurantFeedback]:
        """Get all feedback from a specific user."""
        return self.db.query(RestaurantFeedback).filter(RestaurantFeedback.user_id == user_id).all()
