import { api } from './api';
import { MenuItem, Category, MenuItemCreate, MenuItemUpdate, CategoryCreate, CategoryUpdate, Allergen } from '../types/menu';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Helper function to ensure image URLs are absolute
const ensureAbsoluteImageUrl = (item: MenuItem): MenuItem => {
  if (item.image_url && !item.image_url.startsWith('http')) {
    return {
      ...item,
      image_url: `${API_URL}${item.image_url}`
    };
  }
  return item;
};

class MenuService {
  async getMenuItems(categoryId?: number, activeOnly: boolean = true): Promise<MenuItem[]> {
    const params = new URLSearchParams();
    if (categoryId) params.append('category_id', categoryId.toString());
    if (activeOnly) params.append('active_only', 'true');
    
    console.log('Making API call to get menu items with params:', params.toString());
    const response = await api.get(`/api/menu/items/`, { params });
    console.log('API response for menu items:', response.data);
    return response.data.map(ensureAbsoluteImageUrl);
  }

  async getMenuItem(id: number): Promise<MenuItem> {
    const response = await api.get(`/api/menu/items/${id}`);
    return ensureAbsoluteImageUrl(response.data);
  }

  async createMenuItem(data: MenuItemCreate): Promise<MenuItem> {
    console.log('Creating menu item with data:', data);
    const response = await api.post('/api/menu/items/', data);
    console.log('Create response:', response.data);
    return response.data;
  }

  async updateMenuItem(id: number, data: MenuItemUpdate): Promise<MenuItem> {
    console.log('updateMenuItem - Request URL:', `/api/menu/items/${id}`);
    console.log('updateMenuItem - Request data:', JSON.stringify(data, null, 2));
    
    try {
      const response = await api.patch(`/api/menu/items/${id}/`, data);
      console.log('updateMenuItem - Response:', response.data);
      return response.data;
    } catch (error) {
      console.error('updateMenuItem - Error:', error);
      throw error;
    }
  }

  async deleteMenuItem(id: number): Promise<void> {
    await api.delete(`/api/menu/items/${id}`);
  }

  async getCategories(activeOnly: boolean = true): Promise<Category[]> {
    const params = new URLSearchParams();
    if (activeOnly) params.append('active_only', 'true');
    const response = await api.get(`/api/menu/categories`, { params });
    return response.data;
  }

  async getCategory(id: number): Promise<Category> {
    const response = await api.get(`/api/menu/categories/${id}`);
    return response.data;
  }

  async createCategory(data: CategoryCreate): Promise<Category> {
    const response = await api.post(`/api/menu/categories`, data);
    return response.data;
  }

  async updateCategory(id: number, data: CategoryUpdate): Promise<Category> {
    const response = await api.patch(`/api/menu/categories/${id}`, data);
    return response.data;
  }

  async deleteCategory(id: number): Promise<void> {
    await api.delete(`/api/menu/categories/${id}`);
  }

  async uploadImage(id: number, file: File): Promise<MenuItem> {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post(`/api/menu/items/${id}/image`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return ensureAbsoluteImageUrl(response.data);
  }

  async getAllergens(): Promise<Allergen[]> {
    console.log('Fetching allergens...');
    const response = await api.get(`/api/menu/allergens`);
    console.log('Allergens response:', response.data);
    return response.data;
  }
}

export const menuService = new MenuService(); 