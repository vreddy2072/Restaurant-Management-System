import { api } from './api';
import { API_ROUTES } from '../constants/api';

export interface OrderCreate {
  customer_name: string;
  is_group_order: boolean;
}

export interface OrderResponse {
  id: number;
  order_number: string;
  user_id: number;
  table_number: number;
  customer_name: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export const createOrder = async (orderData: OrderCreate): Promise<OrderResponse> => {
  try {
    console.log('Making order request with data:', orderData);
    const response = await api.post(API_ROUTES.orders.create, orderData);
    console.log('Order creation response:', response.data);
    return response.data;
  } catch (error: any) {
    console.error('Error creating order:', {
      error,
      response: error.response,
      data: error.response?.data,
      status: error.response?.status,
      message: error.message
    });
    if (error.response?.status === 401) {
      throw new Error('Authentication required. Please try again.');
    }
    throw error;
  }
}; 