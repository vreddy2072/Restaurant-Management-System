from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging
from datetime import datetime
from typing import Optional

from backend.models.schemas.cart import CartResponse, CartItemCreate, CartItemUpdate
from backend.services.cart_service import CartService
from backend.utils.database import get_db
from backend.utils.auth import get_current_user
from backend.models.schemas.user import UserResponse

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/cart", tags=["cart"])

@router.get("", response_model=CartResponse)
async def get_cart(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the current user's shopping cart"""
    try:
        # Require authentication
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        
        logger.debug(f"Fetching cart for user {current_user.id}")
        service = CartService(db)
        cart = service.get_or_create_cart(current_user.id)
        return cart
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching cart: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/items", response_model=CartResponse)
async def add_item_to_cart(
    item: CartItemCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add an item to the shopping cart"""
    try:
        logger.debug(f"Adding item to cart for user {current_user.id}: {item}")
        service = CartService(db)
        cart = service.add_item(current_user.id, item)
        return cart
    except ValueError as e:
        logger.error(f"Validation error adding item to cart: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error adding item to cart: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/items/{item_id}", response_model=CartResponse)
async def update_cart_item(
    item_id: int,
    item_update: CartItemUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a cart item's quantity or customizations"""
    try:
        logger.debug(f"Updating cart item {item_id} for user {current_user.id}: {item_update}")
        service = CartService(db)
        cart = service.update_item(current_user.id, item_id, item_update)
        return cart
    except ValueError as e:
        logger.error(f"Validation error updating cart item: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating cart item: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/items/{item_id}", response_model=CartResponse)
async def remove_cart_item(
    item_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove an item from the shopping cart"""
    try:
        logger.debug(f"Removing item {item_id} from cart for user {current_user.id}")
        service = CartService(db)
        cart = service.remove_item(current_user.id, item_id)
        return cart
    except ValueError as e:
        logger.error(f"Validation error removing cart item: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error removing cart item: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("", response_model=CartResponse)
async def clear_cart(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Clear all items from the shopping cart"""
    try:
        logger.debug(f"Clearing cart for user {current_user.id}")
        service = CartService(db)
        cart = service.clear_cart(current_user.id)
        return cart
    except Exception as e:
        logger.error(f"Error clearing cart: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/total", response_model=float)
async def get_cart_total(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the total price of all items in the cart"""
    try:
        logger.debug(f"Calculating cart total for user {current_user.id}")
        service = CartService(db)
        total = service.calculate_total(current_user.id)
        return total
    except Exception as e:
        logger.error(f"Error calculating cart total: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
