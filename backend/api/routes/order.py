from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.models.schemas.order import OrderCreate, OrderUpdate, OrderResponse
from backend.services.order_service import OrderService
from backend.services.cart_service import CartService
from backend.utils.database import get_db
from backend.utils.auth import get_current_user
from backend.models.orm.user import User
from backend.utils.exceptions import NotFoundException, ValidationError

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/create", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    order_data: OrderCreate,
    cart_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new order and optionally link it to a cart"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
        
    try:
        service = OrderService(db)
        cart_service = CartService(db)
        
        # Create the order
        order = service.create_order(current_user.id, order_data)
        
        # If cart_id is provided, link the cart to the order
        if cart_id is not None:
            cart = cart_service.get_cart(cart_id)
            if cart.user_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to use this cart"
                )
            cart.order_number = order.order_number
            db.commit()
        
        return order
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/get_order_by_id/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get order by ID"""
    try:
        service = OrderService(db)
        order = service.get_order(order_id)
        
        # Only allow users to view their own orders unless they're staff
        if order.user_id != current_user.id and not current_user.is_staff:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this order"
            )
        return order
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.get("/get_order_by_number/{order_number}", response_model=OrderResponse)
def get_order_by_number(
    order_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get order by order number"""
    try:
        service = OrderService(db)
        order = service.get_order_by_number(order_number)
        
        # Only allow users to view their own orders unless they're staff
        if order.user_id != current_user.id and not current_user.is_staff:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this order"
            )
        return order
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.get("/get_orders", response_model=List[OrderResponse])
def get_user_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all orders for the current user"""
    service = OrderService(db)
    return service.get_user_orders(current_user.id)

@router.put("/update_order/{order_id}", response_model=OrderResponse)
def update_order(
    order_id: int,
    order_data: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update order details"""
    try:
        service = OrderService(db)
        order = service.get_order(order_id)
        
        # Only allow users to update their own orders unless they're staff
        if order.user_id != current_user.id and not current_user.is_staff:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this order"
            )
        
        updated_order = service.update_order(order_id, order_data)
        return updated_order
    except (NotFoundException, ValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/cancel_order/{order_id}", response_model=OrderResponse)
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel an order"""
    try:
        service = OrderService(db)
        order = service.get_order(order_id)
        
        # Only allow users to cancel their own orders unless they're staff
        if order.user_id != current_user.id and not current_user.is_staff:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to cancel this order"
            )
        
        cancelled_order = service.cancel_order(order_id)
        return cancelled_order
    except (NotFoundException, ValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/confirm_order/{order_id}", response_model=OrderResponse)
def confirm_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Confirm an order"""
    try:
        service = OrderService(db)
        order = service.get_order(order_id)
        
        # Only allow users to confirm their own orders
        if order.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to confirm this order"
            )
        
        confirmed_order = service.confirm_order(order_id)
        return confirmed_order
    except (NotFoundException, ValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/get_orders_by_status/{status}", response_model=List[OrderResponse])
def get_orders_by_status(
    status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get orders by status (staff only)"""
    if not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff members can view all orders"
        )
    
    try:
        service = OrderService(db)
        return service.get_orders_by_status(status)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) 