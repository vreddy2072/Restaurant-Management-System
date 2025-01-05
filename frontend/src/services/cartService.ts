import { api } from './api';
import { Cart, CartItem, AddToCartRequest, UpdateCartItemRequest, CartTotal } from '../types/cart';

class CartService {
  async getCart(): Promise<Cart> {
    const response = await api.get('/api/cart');
    return response.data;
  }

  async clearCart(): Promise<void> {
    await api.delete('/api/cart');
  }

  async addItem(data: AddToCartRequest): Promise<Cart> {
    const response = await api.post('/api/cart/items', data);
    return response.data;
  }

  async updateItem(itemId: number, data: UpdateCartItemRequest): Promise<Cart> {
    const response = await api.put(`/api/cart/items/${itemId}`, data);
    return response.data;
  }

  async removeItem(itemId: number): Promise<Cart> {
    const response = await api.delete(`/api/cart/items/${itemId}`);
    return response.data;
  }

  async getTotal(): Promise<CartTotal> {
    const response = await api.get('/api/cart/total');
    return response.data;
  }
}

export const cartService = new CartService();
