import { api } from './api';

export interface MenuItemRating {
  id: number;
  user_id: number;
  menu_item_id: number;
  rating: number;
  comment: string;
  created_at: string;
  updated_at: string;
}

export interface RestaurantFeedback {
  id: number;
  user_id: number;
  feedback_text: string;
  service_rating: number;
  ambiance_rating: number;
  cleanliness_rating: number;
  value_rating: number;
  created_at: string;
  updated_at: string;
}

export interface RestaurantFeedbackStats {
  average_service_rating: number;
  average_ambiance_rating: number;
  average_cleanliness_rating: number;
  average_value_rating: number;
  total_reviews: number;
}

export interface MenuItemRatingCreate {
  menu_item_id: number;
  rating: number;
  comment?: string;
}

export interface RestaurantFeedbackCreate {
  feedback_text: string;
  service_rating: number;
  ambiance_rating: number;
  cleanliness_rating: number;
  value_rating: number;
}

const feedbackService = {
  // Menu Item Ratings
  rateMenuItem: async (data: MenuItemRatingCreate) => {
    const response = await api.post(`/api/ratings/menu-items/${data.menu_item_id}`, data);
    return response.data;
  },

  getMenuItemRatings: async (menuItemId: number) => {
    const response = await api.get(`/api/ratings/menu-items/${menuItemId}`);
    return response.data;
  },

  deleteMenuItemRating: async (menuItemId: number) => {
    await api.delete(`/api/ratings/menu-items/${menuItemId}`);
  },

  getUserMenuItemRating: async (menuItemId: number) => {
    const response = await api.get(`/api/ratings/menu-items/${menuItemId}/user`);
    return response.data;
  },

  getMenuItemAverageRating: async (menuItemId: number) => {
    const response = await api.get(`/api/ratings/menu-items/${menuItemId}/average`);
    return response.data;
  },

  // Restaurant Feedback
  getRestaurantFeedback: async () => {
    const response = await api.get('/api/ratings/restaurant-feedback');
    return response.data;
  },

  createRestaurantFeedback: async (data: RestaurantFeedbackCreate) => {
    const response = await api.post('/api/ratings/restaurant-feedback', data);
    return response.data;
  },

  getUserRestaurantFeedback: async () => {
    const response = await api.get('/api/ratings/restaurant-feedback/user');
    return response.data;
  },

  getRestaurantFeedbackStats: async () => {
    const response = await api.get('/api/ratings/restaurant-feedback/stats');
    return response.data;
  },

  getRecentRestaurantFeedback: async () => {
    const response = await api.get('/api/ratings/restaurant-feedback/recent');
    return response.data;
  },
};

export default feedbackService; 