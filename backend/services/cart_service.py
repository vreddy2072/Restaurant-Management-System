from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from backend.models.orm.shopping_cart import ShoppingCart, CartItem
from backend.models.orm.menu import MenuItem
from backend.models.schemas.cart import CartItemCreate, CartItemUpdate
from backend.utils.exceptions import NotFoundException, ValidationError

class CartService:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create_cart(self, user_id: int) -> ShoppingCart:
        """Get active cart for user or create new one if none exists"""
        # Look for an active cart (no order_number means it's not linked to an order)
        cart = self.db.query(ShoppingCart).filter(
            ShoppingCart.user_id == user_id,
            ShoppingCart.order_number == None
        ).first()

        if not cart:
            # Create new cart if none exists
            cart = ShoppingCart(user_id=user_id)
            self.db.add(cart)
            self.db.commit()
            self.db.refresh(cart)

        return cart

    def get_cart(self, cart_id: int) -> ShoppingCart:
        """Get cart by ID"""
        cart = self.db.query(ShoppingCart).filter(ShoppingCart.id == cart_id).first()
        if not cart:
            raise NotFoundException(f"Cart with id {cart_id} not found")
        return cart

    def get_user_cart(self, user_id: int) -> Optional[ShoppingCart]:
        """Get user's active cart"""
        return self.db.query(ShoppingCart).filter(
            ShoppingCart.user_id == user_id,
            ShoppingCart.order_number == None
        ).first()

    def get_cart_by_order(self, order_number: str) -> Optional[ShoppingCart]:
        """Get cart associated with an order"""
        return self.db.query(ShoppingCart).filter(
            ShoppingCart.order_number == order_number
        ).first()

    def add_item(self, cart_id: int, item_data: CartItemCreate) -> ShoppingCart:
        """Add item to cart"""
        cart = self.get_cart(cart_id)
        
        # Check if cart is already linked to an order
        if cart.order_number:
            raise ValidationError("Cannot modify cart that is linked to an order")

        # Verify menu item exists
        menu_item = self.db.query(MenuItem).filter(MenuItem.id == item_data.menu_item_id).first()
        if not menu_item:
            raise NotFoundException(f"Menu item with id {item_data.menu_item_id} not found")

        try:
            # Check if item already exists in cart
            cart_item = self.db.query(CartItem).filter(
                CartItem.cart_id == cart_id,
                CartItem.menu_item_id == item_data.menu_item_id
            ).first()

            if cart_item:
                # Update quantity if item exists
                cart_item.quantity += item_data.quantity
                if item_data.customizations is not None:
                    cart_item.customizations = item_data.customizations
            else:
                # Create new cart item if it doesn't exist
                cart_item = CartItem(
                    cart_id=cart_id,
                    menu_item_id=item_data.menu_item_id,
                    quantity=item_data.quantity,
                    customizations=item_data.customizations
                )
                self.db.add(cart_item)

            self.db.commit()
            self.db.refresh(cart)
            return cart

        except IntegrityError as e:
            self.db.rollback()
            raise ValidationError(f"Error adding item to cart: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise ValidationError(f"Unexpected error adding item to cart: {str(e)}")

    def update_item(self, cart_id: int, item_id: int, item_data: CartItemUpdate) -> ShoppingCart:
        """Update cart item"""
        cart = self.get_cart(cart_id)
        
        # Check if cart is already linked to an order
        if cart.order_number:
            raise ValidationError("Cannot modify cart that is linked to an order")

        cart_item = self.db.query(CartItem).filter(
            CartItem.id == item_id,
            CartItem.cart_id == cart_id
        ).first()
        if not cart_item:
            raise NotFoundException(f"Cart item with id {item_id} not found in cart {cart_id}")

        try:
            if item_data.quantity is not None:
                cart_item.quantity = item_data.quantity
            if item_data.customizations is not None:
                cart_item.customizations = item_data.customizations

            self.db.commit()
            self.db.refresh(cart)
            return cart

        except IntegrityError as e:
            self.db.rollback()
            raise ValidationError(f"Error updating cart item: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise ValidationError(f"Unexpected error updating cart item: {str(e)}")

    def remove_item(self, cart_id: int, item_id: int) -> ShoppingCart:
        """Remove item from cart"""
        cart = self.get_cart(cart_id)
        
        # Check if cart is already linked to an order
        if cart.order_number:
            raise ValidationError("Cannot modify cart that is linked to an order")

        cart_item = self.db.query(CartItem).filter(
            CartItem.id == item_id,
            CartItem.cart_id == cart_id
        ).first()
        if not cart_item:
            raise NotFoundException(f"Cart item with id {item_id} not found in cart {cart_id}")

        try:
            self.db.delete(cart_item)
            self.db.commit()
            self.db.refresh(cart)
            return cart

        except IntegrityError as e:
            self.db.rollback()
            raise ValidationError(f"Error removing item from cart: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise ValidationError(f"Unexpected error removing item from cart: {str(e)}")

    def clear_cart(self, cart_id: int) -> ShoppingCart:
        """Remove all items from cart"""
        cart = self.get_cart(cart_id)
        
        # Check if cart is already linked to an order
        if cart.order_number:
            raise ValidationError("Cannot modify cart that is linked to an order")

        try:
            self.db.query(CartItem).filter(CartItem.cart_id == cart_id).delete()
            self.db.commit()
            self.db.refresh(cart)
            return cart

        except IntegrityError as e:
            self.db.rollback()
            raise ValidationError(f"Error clearing cart: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise ValidationError(f"Unexpected error clearing cart: {str(e)}")

    def calculate_cart_total(self, cart_id: int) -> float:
        """Calculate total price of items in cart"""
        cart = self.get_cart(cart_id)
        total = 0.0

        for item in cart.cart_items:
            total += item.menu_item.price * item.quantity

        return total 