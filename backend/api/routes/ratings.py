from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict

from backend.utils.database import get_db
from backend.utils.auth import get_current_user
from backend.services.rating_service import RatingService
from backend.models.schemas.rating import MenuItemRatingCreate, MenuItemRatingResponse
from backend.models.schemas.user import UserResponse

router = APIRouter(prefix="/api/ratings", tags=["ratings"])

@router.post("/menu-items/{menu_item_id}", response_model=MenuItemRatingResponse)
def rate_menu_item(
    menu_item_id: int,
    rating: MenuItemRatingCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create or update a rating for a menu item"""
    service = RatingService(db)
    try:
        return service.create_menu_item_rating(rating, current_user.id)
    except ValueError as e:
        # If rating exists, try to update it
        return service.update_menu_item_rating(current_user.id, menu_item_id, rating)

@router.get("/menu-items/{menu_item_id}", response_model=List[MenuItemRatingResponse])
def get_menu_item_ratings(
    menu_item_id: int,
    db: Session = Depends(get_db)
):
    """Get all ratings for a menu item"""
    service = RatingService(db)
    return service.get_menu_item_ratings(menu_item_id)

@router.get("/menu-items/{menu_item_id}/user", response_model=MenuItemRatingResponse)
def get_user_menu_item_rating(
    menu_item_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the current user's rating for a menu item"""
    service = RatingService(db)
    rating = service.get_user_menu_item_rating(current_user.id, menu_item_id)
    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rating not found"
        )
    return rating

@router.delete("/menu-items/{menu_item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_menu_item_rating(
    menu_item_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a user's rating for a menu item"""
    service = RatingService(db)
    if not service.delete_menu_item_rating(current_user.id, menu_item_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rating not found"
        )

@router.get("/menu-items/{menu_item_id}/average", response_model=Dict[str, float])
def get_menu_item_average_rating(
    menu_item_id: int,
    db: Session = Depends(get_db)
):
    """Get the average rating for a menu item"""
    service = RatingService(db)
    ratings = service.get_menu_item_ratings(menu_item_id)
    if not ratings:
        return {"average": 0.0, "total": 0}
    
    total = len(ratings)
    average = sum(r.rating for r in ratings) / total
    return {"average": round(average, 1), "total": total}