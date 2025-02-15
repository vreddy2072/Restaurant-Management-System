import { api } from './api';
import { MenuItem, Category, MenuItemCreate, MenuItemUpdate, CategoryCreate, CategoryUpdate, Allergen } from '../types/menu';
import { API_ROUTES } from '../constants/api';

// In production, use relative path which will be handled by Vercel rewrites
// In development, use the full localhost URL
const isDevelopment = import.meta.env.MODE === 'development';
const API_URL = isDevelopment ? 'http://localhost:8000' : '';

// Helper function to ensure image URLs are absolute
const ensureAbsoluteImageUrl = (item: MenuItem): MenuItem => {
  if (!item.image_url) return item;
  
  // If it's already an absolute URL, return as is
  if (item.image_url.startsWith('http')) {
    return item;
  }

  // If it's a relative URL starting with /static, append to API URL
  if (item.image_url.startsWith('/static')) {
    const baseUrl = isDevelopment ? API_URL : 'https://restaurant-management-system-5c3x.onrender.com';
    return {
      ...item,
      image_url: `${baseUrl}${item.image_url}`
    };
  }

  // If it's a relative URL without /static, assume it's a static file
  return {
    ...item,
    image_url: `${API_URL}/static/${item.image_url}`
  };
};

class MenuService {
  async getMenuItems(categoryId?: number, activeOnly: boolean = true): Promise<MenuItem[]> {
    const params = new URLSearchParams();
    if (categoryId) params.append('category_id', categoryId.toString());
    if (activeOnly) params.append('active_only', 'true');
    
    console.log('Fetching menu items with params:', params.toString());
    try {
      const response = await api.get(API_ROUTES.menu.items, { params });
      console.log('Menu items response:', response.data);
      return response.data.map(ensureAbsoluteImageUrl);
    } catch (error) {
      console.error('Failed to fetch menu items:', error);
      throw error;
    }
  }

  async getMenuItem(id: number): Promise<MenuItem> {
    console.log(`Fetching menu item with ID: ${id}`);
    try {
      const response = await api.get(`${API_ROUTES.menu.items}/${id}`);
      console.log('Menu item response:', response.data);
      return ensureAbsoluteImageUrl(response.data);
    } catch (error) {
      console.error(`Failed to fetch menu item ${id}:`, error);
      throw error;
    }
  }

  async createMenuItem(data: MenuItemCreate): Promise<MenuItem> {
    console.log('Creating menu item with data:', data);
    try {
      const response = await api.post(API_ROUTES.menu.items, data);
      console.log('Create menu item response:', response.data);
      return response.data;
    } catch (error) {
      console.error('Failed to create menu item:', error);
      throw error;
    }
  }

  async updateMenuItem(id: number, data: MenuItemUpdate): Promise<MenuItem> {
    console.log(`Updating menu item ${id} with data:`, data);
    try {
      const response = await api.patch(`${API_ROUTES.menu.items}/${id}`, data, {
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      });
      console.log('Update menu item response:', response.data);
      return response.data;
    } catch (error: any) {
      console.error(`Failed to update menu item ${id}:`, error);
      if (error.response) {
        console.error('Error response:', {
          status: error.response.status,
          data: error.response.data,
          headers: error.response.headers
        });
      }
      throw error;
    }
  }

  async deleteMenuItem(id: number): Promise<void> {
    console.log(`Deleting menu item ${id}`);
    try {
      await api.delete(`${API_ROUTES.menu.items}/${id}`, {
        headers: {
          'Accept': 'application/json'
        }
      });
      console.log(`Menu item ${id} deleted successfully`);
    } catch (error: any) {
      console.error(`Failed to delete menu item ${id}:`, error);
      if (error.response) {
        console.error('Error response:', {
          status: error.response.status,
          data: error.response.data,
          headers: error.response.headers
        });
      }
      throw error;
    }
  }

  async getCategories(activeOnly: boolean = true): Promise<Category[]> {
    const params = new URLSearchParams();
    if (activeOnly) params.append('active_only', 'true');
    console.log('Fetching categories with params:', params.toString());
    try {
      const response = await api.get(API_ROUTES.menu.categories, { params });
      console.log('Categories response:', response.data);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch categories:', error);
      throw error;
    }
  }

  async getCategory(id: number): Promise<Category> {
    const response = await api.get(`${API_ROUTES.menu.categories}/${id}`);
    return response.data;
  }

  async createCategory(data: CategoryCreate): Promise<Category> {
    const response = await api.post(API_ROUTES.menu.categories, data);
    return response.data;
  }

  async updateCategory(id: number, data: CategoryUpdate): Promise<Category> {
    try {
      const response = await api.patch(`${API_ROUTES.menu.categories}/${id}`, data, {
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      });
      return response.data;
    } catch (error: any) {
      console.error(`Failed to update category ${id}:`, error);
      if (error.response) {
        console.error('Error response:', {
          status: error.response.status,
          data: error.response.data,
          headers: error.response.headers
        });
      }
      throw error;
    }
  }

  async deleteCategory(id: number): Promise<void> {
    try {
      await api.delete(`${API_ROUTES.menu.categories}/${id}`, {
        headers: {
          'Accept': 'application/json'
        }
      });
    } catch (error: any) {
      console.error(`Failed to delete category ${id}:`, error);
      if (error.response) {
        console.error('Error response:', {
          status: error.response.status,
          data: error.response.data,
          headers: error.response.headers
        });
      }
      throw error;
    }
  }

  async uploadImage(id: number, file: File): Promise<MenuItem> {
    console.log(`Uploading image for menu item ${id}`);
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await api.post(`${API_ROUTES.menu.items}/${id}/image`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'Accept': 'application/json'
        },
        // Needed for proper FormData handling
        transformRequest: [(data) => data]
      });
      console.log('Upload image response:', response.data);
      return ensureAbsoluteImageUrl(response.data);
    } catch (error: any) {
      console.error('Failed to upload image:', error);
      if (error.response) {
        console.error('Error response:', {
          status: error.response.status,
          data: error.response.data,
          headers: error.response.headers
        });
      }
      throw error;
    }
  }

  async getAllergens(): Promise<Allergen[]> {
    console.log('Fetching allergens...');
    try {
      const response = await api.get(API_ROUTES.menu.allergens);
      console.log('Allergens response:', response.data);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch allergens:', error);
      throw error;
    }
  }
}

export const menuService = new MenuService(); 