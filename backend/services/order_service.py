import random
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc

from backend.models.orm.order import Order
from backend.models.orm.user import User
from backend.models.orm.shopping_cart import ShoppingCart
from backend.models.schemas.order import OrderCreate, OrderUpdate, OrderStatus
from backend.utils.exceptions import NotFoundException, ValidationError

class OrderService:
    def __init__(self, db: Session):
        self.db = db

    def _generate_order_number(self) -> str:
        """Generate a unique order number"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M")
        random_num = random.randint(1000, 9999)
        return f"ORD-{timestamp}-{random_num}"

    def _get_random_table(self) -> int:
        """Get a random table number between 1 and 10"""
        return random.randint(1, 10)

    def create_order(self, user_id: int, order_data: OrderCreate) -> Order:
        """Create a new order"""
        try:
            # Generate unique order number and random table
            order_number = self._generate_order_number()
            table_number = self._get_random_table()

            # Create order
            order = Order(
                order_number=order_number,
                table_number=table_number,
                customer_name=order_data.customer_name,
                is_group_order=order_data.is_group_order,
                user_id=user_id,
                status=OrderStatus.INITIALIZED
            )
            self.db.add(order)
            self.db.commit()
            self.db.refresh(order)
            return order

        except IntegrityError as e:
            self.db.rollback()
            raise ValidationError(f"Error creating order: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise ValidationError(f"Unexpected error creating order: {str(e)}")

    def get_order(self, order_id: int) -> Order:
        """Get order by ID"""
        order = self.db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise NotFoundException(f"Order with id {order_id} not found")
        return order

    def get_order_by_number(self, order_number: str) -> Order:
        """Get order by order number"""
        order = self.db.query(Order).filter(Order.order_number == order_number).first()
        if not order:
            raise NotFoundException(f"Order with number {order_number} not found")
        return order

    def get_user_orders(self, user_id: int) -> List[Order]:
        """Get all orders for a user"""
        return self.db.query(Order).filter(Order.user_id == user_id).order_by(desc(Order.created_at)).all()

    def update_order(self, order_id: int, order_data: OrderUpdate) -> Order:
        """Update order details"""
        order = self.get_order(order_id)

        try:
            # Update status if provided
            if order_data.status is not None:
                order.status = order_data.status

            self.db.commit()
            self.db.refresh(order)
            return order

        except IntegrityError as e:
            self.db.rollback()
            raise ValidationError(f"Error updating order: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise ValidationError(f"Unexpected error updating order: {str(e)}")

    def cancel_order(self, order_id: int) -> Order:
        """Cancel an order"""
        order = self.get_order(order_id)
        
        if order.status in [OrderStatus.COMPLETED, OrderStatus.CANCELLED]:
            raise ValidationError(f"Cannot cancel order in {order.status} status")

        order.status = OrderStatus.CANCELLED
        self.db.commit()
        self.db.refresh(order)
        return order

    def get_active_orders(self) -> List[Order]:
        """Get all active orders (not completed or cancelled)"""
        return self.db.query(Order).filter(
            Order.status.in_([
                OrderStatus.INITIALIZED,
                OrderStatus.IN_PROGRESS,
                OrderStatus.CONFIRMED
            ])
        ).order_by(desc(Order.created_at)).all()

    def get_orders_by_status(self, status: OrderStatus) -> List[Order]:
        """Get orders by status"""
        return self.db.query(Order).filter(
            Order.status == status
        ).order_by(desc(Order.created_at)).all()

    def link_cart_to_order(self, order_id: int, cart_id: int) -> Order:
        """Link a shopping cart to an order"""
        order = self.get_order(order_id)
        
        # Verify cart exists and belongs to the same user
        cart = self.db.query(ShoppingCart).filter(
            ShoppingCart.id == cart_id,
            ShoppingCart.user_id == order.user_id
        ).first()
        if not cart:
            raise ValidationError("Invalid cart_id or cart belongs to different user")

        try:
            # Update cart with order number
            cart.order_number = order.order_number
            order.status = OrderStatus.IN_PROGRESS
            self.db.commit()
            self.db.refresh(order)
            return order

        except IntegrityError as e:
            self.db.rollback()
            raise ValidationError(f"Error linking cart to order: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise ValidationError(f"Unexpected error linking cart to order: {str(e)}")

    def confirm_order(self, order_id: int) -> Order:
        """Confirm an order"""
        order = self.get_order(order_id)
        
        if order.status != OrderStatus.IN_PROGRESS:
            raise ValidationError(f"Can only confirm orders in IN_PROGRESS status. Current status: {order.status}")
        
        # Check if any cart is linked to this order
        cart = self.db.query(ShoppingCart).filter(
            ShoppingCart.order_number == order.order_number
        ).first()
        if not cart:
            raise ValidationError("Cannot confirm order without a shopping cart")

        order.status = OrderStatus.CONFIRMED
        self.db.commit()
        self.db.refresh(order)
        return order 