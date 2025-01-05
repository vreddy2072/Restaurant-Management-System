from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from backend.models.orm.shopping_cart import ShoppingCart, CartItem
from backend.models.orm.menu import MenuItem
from backend.models.schemas.cart import CartItemCreate, CartItemUpdate

class CartService:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create_cart(self, user_id: int) -> ShoppingCart:
        """Get the user's shopping cart or create a new one if it doesn't exist."""
        cart = self.db.query(ShoppingCart).filter(ShoppingCart.user_id == user_id).first()
        if not cart:
            cart = ShoppingCart(user_id=user_id)
            self.db.add(cart)
            self.db.commit()
            self.db.refresh(cart)
        return cart

    def get_cart_items(self, user_id: int) -> List[CartItem]:
        """Get all items in the user's shopping cart."""
        cart = self.get_or_create_cart(user_id)
        return cart.items

    def add_item_to_cart(self, user_id: int, item: CartItemCreate) -> CartItem:
        """Add an item to the shopping cart."""
        # Verify menu item exists
        menu_item = self.db.query(MenuItem).filter(MenuItem.id == item.menu_item_id).first()
        if not menu_item:
            raise ValueError("Menu item not found")

        cart = self.get_or_create_cart(user_id)
        
        # Check if item already exists in cart
        existing_item = self.db.query(CartItem).filter(
            CartItem.cart_id == cart.id,
            CartItem.menu_item_id == item.menu_item_id
        ).first()

        if existing_item:
            # Update quantity and customizations if item exists
            existing_item.quantity += item.quantity
            if item.customizations:
                existing_item.customizations = item.customizations
            self.db.commit()
            self.db.refresh(existing_item)
            return existing_item

        # Create new cart item
        cart_item = CartItem(
            cart_id=cart.id,
            menu_item_id=item.menu_item_id,
            quantity=item.quantity,
            customizations=item.customizations
        )
        self.db.add(cart_item)
        self.db.commit()
        self.db.refresh(cart_item)
        return cart_item

    def update_cart_item(self, user_id: int, item_id: int, update_data: CartItemUpdate) -> CartItem:
        """Update quantity or customizations of a cart item."""
        cart = self.get_or_create_cart(user_id)
        cart_item = self.db.query(CartItem).filter(
            CartItem.id == item_id,
            CartItem.cart_id == cart.id
        ).first()

        if not cart_item:
            raise ValueError("Cart item not found")

        if update_data.quantity is not None:
            cart_item.quantity = update_data.quantity
        if update_data.customizations is not None:
            cart_item.customizations = update_data.customizations

        self.db.commit()
        self.db.refresh(cart_item)
        return cart_item

    def remove_item_from_cart(self, user_id: int, item_id: int) -> bool:
        """Remove an item from the shopping cart."""
        cart = self.get_or_create_cart(user_id)
        cart_item = self.db.query(CartItem).filter(
            CartItem.id == item_id,
            CartItem.cart_id == cart.id
        ).first()

        if not cart_item:
            return False

        self.db.delete(cart_item)
        self.db.commit()
        return True

    def clear_cart(self, user_id: int) -> bool:
        """Remove all items from the shopping cart."""
        cart = self.get_or_create_cart(user_id)
        self.db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
        self.db.commit()
        return True

    def get_cart_total(self, user_id: int) -> float:
        """Calculate the total price of all items in the cart."""
        cart_items = self.get_cart_items(user_id)
        total = 0.0
        for item in cart_items:
            total += item.menu_item.price * item.quantity
        return total
