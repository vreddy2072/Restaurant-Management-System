from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func

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
            service_rating=feedback.service_rating,
            ambiance_rating=feedback.ambiance_rating,
            cleanliness_rating=feedback.cleanliness_rating,
            value_rating=feedback.value_rating
        )
        self.db.add(db_feedback)
        self.db.commit()
        self.db.refresh(db_feedback)
        return db_feedback

    def get_restaurant_feedback(self) -> List[RestaurantFeedback]:
        """Get all restaurant feedback."""
        return self.db.query(RestaurantFeedback).all()

    def get_user_feedback(self, user_id: int) -> List[RestaurantFeedback]:
        """Get all feedback from a specific user."""
        return self.db.query(RestaurantFeedback).filter(RestaurantFeedback.user_id == user_id).all()

    def get_restaurant_feedback_stats(self) -> Dict[str, any]:
        """Get statistics for restaurant feedback."""
        result = self.db.query(
            func.avg(RestaurantFeedback.service_rating).label('avg_service'),
            func.avg(RestaurantFeedback.ambiance_rating).label('avg_ambiance'),
            func.avg(RestaurantFeedback.cleanliness_rating).label('avg_cleanliness'),
            func.avg(RestaurantFeedback.value_rating).label('avg_value'),
            func.count(RestaurantFeedback.id).label('total')
        ).first()

        return {
            'average_service_rating': round(float(result.avg_service), 1) if result.avg_service else 0.0,
            'average_ambiance_rating': round(float(result.avg_ambiance), 1) if result.avg_ambiance else 0.0,
            'average_cleanliness_rating': round(float(result.avg_cleanliness), 1) if result.avg_cleanliness else 0.0,
            'average_value_rating': round(float(result.avg_value), 1) if result.avg_value else 0.0,
            'total_reviews': result.total
        }

    def get_recent_feedback(self, limit: int = 5) -> List[RestaurantFeedback]:
        """Get the most recent restaurant feedback."""
        return self.db.query(RestaurantFeedback)\
            .order_by(RestaurantFeedback.created_at.desc())\
            .limit(limit)\
            .all()

    def get_menu_item_average_rating(self, menu_item_id: int) -> Dict[str, any]:
        """Get the average rating and total number of ratings for a menu item."""
        result = self.db.query(
            func.avg(MenuItemRating.rating).label('average'),
            func.count(MenuItemRating.id).label('total')
        ).filter(
            MenuItemRating.menu_item_id == menu_item_id
        ).first()
        
        return {
            'average_rating': round(float(result.average), 1) if result.average else 0.0,
            'total_ratings': result.total
        }

    def get_menu_items_average_ratings(self, menu_item_ids: List[int]) -> Dict[int, Dict[str, any]]:
        """Get average ratings for multiple menu items at once."""
        results = self.db.query(
            MenuItemRating.menu_item_id,
            func.avg(MenuItemRating.rating).label('average'),
            func.count(MenuItemRating.id).label('total')
        ).filter(
            MenuItemRating.menu_item_id.in_(menu_item_ids)
        ).group_by(
            MenuItemRating.menu_item_id
        ).all()
        
        return {
            r.menu_item_id: {
                'average_rating': round(float(r.average), 1),
                'total_ratings': r.total
            }
            for r in results
        }
