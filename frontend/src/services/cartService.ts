import { api } from './api';
import { Cart, CartItem, AddToCartRequest, UpdateCartItemRequest, CartTotal } from '../types/cart';

const MAX_RETRIES = 3;
const RETRY_DELAY = 1000;

// Helper function to ensure image URLs are absolute
const ensureAbsoluteImageUrl = (cart: Cart): Cart => {
  if (!cart.cart_items) return cart;

  const isDevelopment = import.meta.env.VITE_NODE_ENV === 'development';
  const API_URL = isDevelopment ? 'http://localhost:8000' : '';

  return {
    ...cart,
    cart_items: cart.cart_items.map(item => {
      if (!item.menu_item.image_url) return item;

      // If it's already an absolute URL, return as is
      if (item.menu_item.image_url.startsWith('http')) {
        return item;
      }

      // If it's a relative URL starting with /static, append to API URL
      if (item.menu_item.image_url.startsWith('/static')) {
        const baseUrl = isDevelopment ? API_URL : 'https://restaurant-management-system-5c3x.onrender.com';
        return {
          ...item,
          menu_item: {
            ...item.menu_item,
            image_url: `${baseUrl}${item.menu_item.image_url}`
          }
        };
      }

      // If it's a relative URL without /static, assume it's a static file
      return {
        ...item,
        menu_item: {
          ...item.menu_item,
          image_url: `${API_URL}/static/${item.menu_item.image_url}`
        }
      };
    })
  };
};

class CartService {
  private async retryOperation<T>(operation: () => Promise<T>): Promise<T> {
    let lastError: any;
    for (let i = 0; i < MAX_RETRIES; i++) {
      try {
        const result = await operation();
        return result;
      } catch (error) {
        lastError = error;
        if (i < MAX_RETRIES - 1) {
          await new Promise(resolve => setTimeout(resolve, RETRY_DELAY));
        }
      }
    }
    throw lastError;
  }

  async getCart(): Promise<Cart> {
    return this.retryOperation(async () => {
      try {
        const response = await api.get('/api/cart');
        return ensureAbsoluteImageUrl(response.data);
      } catch (error: any) {
        if (error.response?.status === 404) {
          // Return an empty cart with the correct structure
          return {
            id: 0,
            user_id: 0,
            cart_items: [],
            order_number: null,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
          };
        }
        throw error;
      }
    });
  }

  async clearCart(): Promise<void> {
    return this.retryOperation(async () => {
      await api.delete('/api/cart');
    });
  }

  async addItem(data: AddToCartRequest): Promise<Cart> {
    return this.retryOperation(async () => {
      const response = await api.post('/api/cart/items', data);
      return ensureAbsoluteImageUrl(response.data);
    });
  }

  async updateItem(itemId: number, data: UpdateCartItemRequest): Promise<Cart> {
    return this.retryOperation(async () => {
      const response = await api.put(`/api/cart/items/${itemId}`, data);
      return ensureAbsoluteImageUrl(response.data);
    });
  }

  async removeItem(itemId: number): Promise<Cart> {
    return this.retryOperation(async () => {
      const response = await api.delete(`/api/cart/items/${itemId}`);
      return ensureAbsoluteImageUrl(response.data);
    });
  }

  async getTotal(): Promise<CartTotal> {
    return this.retryOperation(async () => {
      const response = await api.get('/api/cart/total');
      return response.data;
    });
  }
}

export const cartService = new CartService();
