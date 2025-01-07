from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

from backend.models.orm.shopping_cart import ShoppingCart, CartItem
from backend.models.orm.menu import MenuItem
from backend.models.schemas.cart import CartItemCreate, CartItemUpdate

logger = logging.getLogger(__name__)

class CartService:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create_cart(self, user_id: int) -> ShoppingCart:
        """Get the user's cart or create one if it doesn't exist"""
        try:
            cart = self.db.query(ShoppingCart).filter(ShoppingCart.user_id == user_id).first()
            if not cart:
                logger.debug(f"Creating new cart for user {user_id}")
                cart = ShoppingCart(user_id=user_id)
                self.db.add(cart)
                self.db.commit()
                self.db.refresh(cart)
            return cart
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_or_create_cart: {str(e)}")
            self.db.rollback()
            raise

    def add_item(self, user_id: int, item_data: CartItemCreate) -> ShoppingCart:
        """Add an item to the cart"""
        try:
            # Verify menu item exists
            menu_item = self.db.query(MenuItem).get(item_data.menu_item_id)
            if not menu_item:
                raise ValueError(f"Menu item {item_data.menu_item_id} not found")
            if not menu_item.is_available:
                raise ValueError(f"Menu item {item_data.menu_item_id} is not available")

            cart = self.get_or_create_cart(user_id)

            # Check if item already exists in cart
            existing_item = self.db.query(CartItem).filter(
                CartItem.cart_id == cart.id,
                CartItem.menu_item_id == item_data.menu_item_id
            ).first()

            if existing_item:
                # Update quantity and customizations
                existing_item.quantity += item_data.quantity
                if item_data.customizations:
                    existing_item.customizations = item_data.customizations
            else:
                # Create new cart item
                cart_item = CartItem(
                    cart_id=cart.id,
                    menu_item_id=item_data.menu_item_id,
                    quantity=item_data.quantity,
                    customizations=item_data.customizations
                )
                self.db.add(cart_item)

            self.db.commit()
            self.db.refresh(cart)
            return cart

        except SQLAlchemyError as e:
            logger.error(f"Database error in add_item: {str(e)}")
            self.db.rollback()
            raise

    def update_item(self, user_id: int, item_id: int, item_update: CartItemUpdate) -> ShoppingCart:
        """Update a cart item's quantity or customizations"""
        try:
            cart = self.get_or_create_cart(user_id)
            cart_item = self.db.query(CartItem).filter(
                CartItem.id == item_id,
                CartItem.cart_id == cart.id
            ).first()

            if not cart_item:
                raise ValueError(f"Cart item {item_id} not found")

            if item_update.quantity is not None:
                if item_update.quantity <= 0:
                    # Remove item if quantity is 0 or negative
                    self.db.delete(cart_item)
                else:
                    cart_item.quantity = item_update.quantity

            if item_update.customizations is not None:
                cart_item.customizations = item_update.customizations

            self.db.commit()
            self.db.refresh(cart)
            return cart

        except SQLAlchemyError as e:
            logger.error(f"Database error in update_item: {str(e)}")
            self.db.rollback()
            raise

    def remove_item(self, user_id: int, item_id: int) -> ShoppingCart:
        """Remove an item from the cart"""
        try:
            cart = self.get_or_create_cart(user_id)
            cart_item = self.db.query(CartItem).filter(
                CartItem.id == item_id,
                CartItem.cart_id == cart.id
            ).first()

            if not cart_item:
                raise ValueError(f"Cart item {item_id} not found")

            self.db.delete(cart_item)
            self.db.commit()
            self.db.refresh(cart)
            return cart

        except SQLAlchemyError as e:
            logger.error(f"Database error in remove_item: {str(e)}")
            self.db.rollback()
            raise

    def clear_cart(self, user_id: int) -> ShoppingCart:
        """Remove all items from the cart"""
        try:
            cart = self.get_or_create_cart(user_id)
            self.db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
            self.db.commit()
            self.db.refresh(cart)
            return cart

        except SQLAlchemyError as e:
            logger.error(f"Database error in clear_cart: {str(e)}")
            self.db.rollback()
            raise

    def calculate_total(self, user_id: int) -> float:
        """Calculate the total price of all items in the cart"""
        try:
            cart = self.get_or_create_cart(user_id)
            total = 0.0

            for item in cart.items:
                menu_item = self.db.query(MenuItem).get(item.menu_item_id)
                if menu_item:
                    total += menu_item.price * item.quantity

            return total

        except SQLAlchemyError as e:
            logger.error(f"Database error in calculate_total: {str(e)}")
            self.db.rollback()
            raise
