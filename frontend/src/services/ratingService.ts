import { api } from './api';
import { API_ROUTES } from '../constants/api';

export interface MenuItemRating {
  id: number;
  user_id: number;
  menu_item_id: number;
  rating: number;
  comment?: string;
  created_at: string;
  updated_at: string;
}

export interface RatingAverage {
  average: number;
  total: number;
}

export interface CreateMenuItemRating {
  menu_item_id: number;
  rating: number;
  comment?: string;
}

class RatingService {
  async createOrUpdateRating(menuItemId: number, rating: number, comment?: string): Promise<MenuItemRating> {
    try {
      const response = await api.post(API_ROUTES.ratings.menuItems.create(menuItemId), {
        menu_item_id: menuItemId,
        rating,
        comment: comment || null
      });
      return response.data;
    } catch (error) {
      console.error('Error creating/updating rating:', error);
      throw error;
    }
  }

  async getMenuItemRatings(menuItemId: number): Promise<MenuItemRating[]> {
    try {
      const response = await api.get(`${API_ROUTES.ratings.menuItems.base}/${menuItemId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching ratings:', error);
      throw error;
    }
  }

  async getUserRating(menuItemId: number): Promise<MenuItemRating | null> {
    try {
      const response = await api.get(API_ROUTES.ratings.menuItems.user(menuItemId));
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 404) {
        return null;
      }
      console.error('Error fetching user rating:', error);
      throw error;
    }
  }

  async deleteRating(menuItemId: number): Promise<void> {
    try {
      await api.delete(`${API_ROUTES.ratings.menuItems.base}/${menuItemId}`);
    } catch (error) {
      console.error('Error deleting rating:', error);
      throw error;
    }
  }

  async getAverageRating(menuItemId: number): Promise<RatingAverage> {
    try {
      const response = await api.get(API_ROUTES.ratings.menuItems.average(menuItemId));
      return response.data;
    } catch (error) {
      console.error('Error fetching average rating:', error);
      return { average: 0, total: 0 };
    }
  }
}

export const ratingService = new RatingService(); 