import { api } from './api';
import { MenuItem, Category, MenuItemCreate, MenuItemUpdate, CategoryCreate, CategoryUpdate } from '../types/menu';

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
    
    const response = await api.get(`/api/menu/items`, { params });
    return response.data.map(ensureAbsoluteImageUrl);
  }

  async getMenuItem(id: number): Promise<MenuItem> {
    const response = await api.get(`/api/menu/items/${id}`);
    return ensureAbsoluteImageUrl(response.data);
  }

  async createMenuItem(data: MenuItemCreate): Promise<MenuItem> {
    const response = await api.post(`/api/menu/items`, data);
    return ensureAbsoluteImageUrl(response.data);
  }

  async updateMenuItem(id: number, data: MenuItemUpdate): Promise<MenuItem> {
    const response = await api.patch(`/api/menu/items/${id}`, data);
    return ensureAbsoluteImageUrl(response.data);
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
}

export const menuService = new MenuService(); 