"""
API routes package
"""
from .users import router as users_router
from .menu import router as menu_router
from .order import router as order_router
from .cart import router as cart_router
from .ratings import router as rating_router