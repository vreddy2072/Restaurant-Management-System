import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { Cart, CartItem, AddToCartRequest, UpdateCartItemRequest } from '../types/cart';
import { cartService } from '../services/cartService';
import { useSnackbar } from '../contexts/SnackbarContext';
import { useAuth } from '../contexts/AuthContext';

interface CartContextType {
  cart: Cart | null;
  loading: boolean;
  error: string | null;
  addToCart: (data: AddToCartRequest) => Promise<void>;
  updateCartItem: (itemId: number, data: UpdateCartItemRequest) => Promise<void>;
  removeFromCart: (itemId: number) => Promise<void>;
  clearCart: () => Promise<void>;
  refreshCart: () => Promise<void>;
}

const CartContext = createContext<CartContextType | undefined>(undefined);

export const CartProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [cart, setCart] = useState<Cart | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { showSnackbar } = useSnackbar();
  const { isAuthenticated, user, guestLogin } = useAuth();

  const refreshCart = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      // If not authenticated, try guest login first
      if (!isAuthenticated) {
        await guestLogin();
      }

      console.log('Refreshing cart...');
      const cartData = await cartService.getCart();
      console.log('Cart refreshed:', cartData);
      
      if (cartData && cartData.cart_items) {
        setCart(cartData);
      } else {
        console.error('Invalid cart data received:', cartData);
        setError('Failed to load cart data');
      }
    } catch (err: any) {
      console.error('Error refreshing cart:', err);
      const errorMessage = err.response?.data?.detail || 'Failed to fetch cart';
      setError(errorMessage);
      showSnackbar(errorMessage, 'error');
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated, showSnackbar, guestLogin]);

  const addToCart = async (data: AddToCartRequest) => {
    try {
      setLoading(true);
      setError(null);

      // If not authenticated, try guest login first
      if (!isAuthenticated) {
        await guestLogin();
      }

      console.log('Adding item to cart:', data);
      const updatedCart = await cartService.addItem(data);
      console.log('Cart updated after adding item:', updatedCart);
      
      if (updatedCart && updatedCart.cart_items) {
        setCart(updatedCart);
        showSnackbar('Item added to cart', 'success');
      } else {
        throw new Error('Invalid cart data received');
      }
    } catch (err: any) {
      console.error('Error adding to cart:', err);
      const errorMessage = err.response?.data?.detail || 'Failed to add item to cart';
      setError(errorMessage);
      showSnackbar(errorMessage, 'error');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const updateCartItem = async (itemId: number, data: UpdateCartItemRequest) => {
    try {
      setLoading(true);
      setError(null);

      // If not authenticated, try guest login first
      if (!isAuthenticated) {
        await guestLogin();
      }

      console.log('Updating cart item:', itemId, data);
      const updatedCart = await cartService.updateItem(itemId, data);
      console.log('Cart updated after updating item:', updatedCart);
      
      if (updatedCart && updatedCart.cart_items) {
        setCart(updatedCart);
        showSnackbar('Cart updated', 'success');
      } else {
        throw new Error('Invalid cart data received');
      }
    } catch (err: any) {
      console.error('Error updating cart:', err);
      const errorMessage = err.response?.data?.detail || 'Failed to update cart';
      setError(errorMessage);
      showSnackbar(errorMessage, 'error');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const removeFromCart = async (itemId: number) => {
    try {
      setLoading(true);
      setError(null);

      // If not authenticated, try guest login first
      if (!isAuthenticated) {
        await guestLogin();
      }

      console.log('Removing item from cart:', itemId);
      const updatedCart = await cartService.removeItem(itemId);
      console.log('Cart updated after removing item:', updatedCart);
      
      if (updatedCart && updatedCart.cart_items) {
        setCart(updatedCart);
        showSnackbar('Item removed from cart', 'success');
      } else {
        throw new Error('Invalid cart data received');
      }
    } catch (err: any) {
      console.error('Error removing from cart:', err);
      const errorMessage = err.response?.data?.detail || 'Failed to remove item from cart';
      setError(errorMessage);
      showSnackbar(errorMessage, 'error');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const clearCart = async () => {
    try {
      setLoading(true);
      setError(null);

      // If not authenticated, try guest login first
      if (!isAuthenticated) {
        await guestLogin();
      }

      console.log('Clearing cart');
      await cartService.clearCart();
      setCart({
        id: 0,
        user_id: 0,
        cart_items: [],
        order_number: null,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      });
      showSnackbar('Cart cleared', 'success');
    } catch (err: any) {
      console.error('Error clearing cart:', err);
      const errorMessage = err.response?.data?.detail || 'Failed to clear cart';
      setError(errorMessage);
      showSnackbar(errorMessage, 'error');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Initialize cart when auth state changes or component mounts
  useEffect(() => {
    if (isAuthenticated) {
      console.log('Auth state changed, refreshing cart. isAuthenticated:', isAuthenticated);
      refreshCart();
    }
  }, [isAuthenticated]); // Only depend on isAuthenticated, not refreshCart

  return (
    <CartContext.Provider
      value={{
        cart,
        loading,
        error,
        addToCart,
        updateCartItem,
        removeFromCart,
        clearCart,
        refreshCart,
      }}
    >
      {children}
    </CartContext.Provider>
  );
};

export const useCart = () => {
  const context = useContext(CartContext);
  if (context === undefined) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
};
