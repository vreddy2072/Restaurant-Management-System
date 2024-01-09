import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { Cart, CartItem, AddToCartRequest, UpdateCartItemRequest } from '../types/cart';
import { cartService } from '../services/cartService';
import { menuService } from '../services/menuService';
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
  const { isAuthenticated } = useAuth();

  const refreshCart = useCallback(async () => {
    if (!isAuthenticated) {
      setCart(null);
      return;
    }
    
    try {
      setLoading(true);
      const cartData = await cartService.getCart();
      
      // Fetch menu items for each cart item
      const menuItems = await menuService.getMenuItems();
      const menuItemsMap = new Map(menuItems.map(item => [item.id, item]));
      
      // Merge menu item data into cart items
      const updatedCart = {
        ...cartData,
        items: cartData.items.map(item => {
          const menuItem = menuItemsMap.get(item.menu_item_id);
          const unit_price = menuItem?.price || 0;
          return {
            ...item,
            unit_price,
            subtotal: unit_price * item.quantity,
            menu_item: {
              name: menuItem?.name || 'Unknown Item',
              description: menuItem?.description || '',
              image_url: menuItem?.image_url,
              customization_options: menuItem?.customization_options,
              price: unit_price
            }
          };
        })
      };
      
      // Calculate total
      const total = updatedCart.items.reduce((sum, item) => sum + item.subtotal, 0);
      updatedCart.total = total;
      
      setCart(updatedCart);
      setError(null);
    } catch (err) {
      setError('Failed to fetch cart');
      showSnackbar('Failed to fetch cart', 'error');
    } finally {
      setLoading(false);
    }
  }, [showSnackbar, isAuthenticated]);

  const addToCart = async (data: AddToCartRequest) => {
    try {
      setLoading(true);
      const updatedCart = await cartService.addItem(data);
      await refreshCart(); // Refresh to get complete menu item data
      showSnackbar('Item added to cart', 'success');
    } catch (err) {
      setError('Failed to add item to cart');
      showSnackbar('Failed to add item to cart', 'error');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const updateCartItem = async (itemId: number, data: UpdateCartItemRequest) => {
    try {
      setLoading(true);
      const updatedCart = await cartService.updateItem(itemId, data);
      await refreshCart(); // Refresh to get complete menu item data
      showSnackbar('Cart updated', 'success');
    } catch (err) {
      setError('Failed to update cart');
      showSnackbar('Failed to update cart', 'error');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const removeFromCart = async (itemId: number) => {
    try {
      setLoading(true);
      const updatedCart = await cartService.removeItem(itemId);
      await refreshCart(); // Refresh to get complete menu item data
      showSnackbar('Item removed from cart', 'success');
    } catch (err) {
      setError('Failed to remove item from cart');
      showSnackbar('Failed to remove item from cart', 'error');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const clearCart = async () => {
    try {
      setLoading(true);
      await cartService.clearCart();
      setCart(null);
      showSnackbar('Cart cleared', 'success');
    } catch (err) {
      setError('Failed to clear cart');
      showSnackbar('Failed to clear cart', 'error');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshCart();
  }, [refreshCart, isAuthenticated]);

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
