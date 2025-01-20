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
from backend.utils.exceptions import NotFoundException

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cart", tags=["cart"])

@router.get("", response_model=CartResponse)
async def get_cart(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the current user's active shopping cart"""
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

@router.get("/order/{order_number}", response_model=CartResponse)
async def get_cart_by_order(
    order_number: str,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a cart by its order number"""
    try:
        logger.debug(f"Fetching cart for order {order_number}")
        service = CartService(db)
        cart = service.get_cart_by_order(order_number)
        
        if not cart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cart not found for order {order_number}"
            )
        
        # Only allow users to view their own carts unless they're staff
        if cart.user_id != current_user.id and not current_user.is_staff:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this cart"
            )
        
        return cart
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching cart by order: {str(e)}")
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
        cart = service.get_or_create_cart(current_user.id)
        
        # Check if cart is linked to an order
        if cart.order_number:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot modify cart that is linked to an order"
            )
        
        try:
            cart = service.add_item(cart.id, item)
            return cart
        except ValueError as e:
            logger.error(f"Validation error adding item to cart: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except NotFoundException as e:
            logger.error(f"Error adding item to cart: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error adding item to cart: {str(e)}")
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
        cart = service.get_or_create_cart(current_user.id)
        
        # Check if cart is linked to an order
        if cart.order_number:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot modify cart that is linked to an order"
            )
        
        cart = service.update_item(cart.id, item_id, item_update)
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
        cart = service.get_or_create_cart(current_user.id)
        
        # Check if cart is linked to an order
        if cart.order_number:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot modify cart that is linked to an order"
            )
        
        cart = service.remove_item(cart.id, item_id)
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
        cart = service.get_or_create_cart(current_user.id)
        
        # Check if cart is linked to an order
        if cart.order_number:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot modify cart that is linked to an order"
            )
        
        cart = service.clear_cart(cart.id)
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
        cart = service.get_or_create_cart(current_user.id)
        total = service.calculate_cart_total(cart.id)
        return total
    except Exception as e:
        logger.error(f"Error calculating cart total: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
