import { api } from './api';
import { API_ROUTES } from '../constants/api';
import {
  UserCreate,
  UserResponse,
  UserLogin,
  AuthResponse,
  UserUpdate
} from '../types/api';

class AuthService {
  async register(data: UserCreate): Promise<UserResponse> {
    try {
      console.log('Starting registration process...');
      const response = await api.post(API_ROUTES.users.register, data);
      return response.data;
    } catch (error: any) {
      console.error('Registration error:', error.response || error);
      if (error.response?.data?.detail) {
        throw new Error(error.response.data.detail);
      }
      throw error;
    }
  }

  async login(data: UserLogin): Promise<AuthResponse> {
    try {
      console.log('Login attempt with:', data);
      const response = await api.post<AuthResponse>(API_ROUTES.users.login, data);
      
      const authData = response.data;
      if (!authData.access_token) {
        throw new Error('No access token in response');
      }
      
      this.setAuthToken(authData.access_token);
      return authData;
    } catch (error: any) {
      console.error('Login error:', error.response || error);
      if (error.response?.data?.detail) {
        throw new Error(error.response.data.detail);
      }
      throw new Error('Login failed: ' + (error.message || 'Unknown error'));
    }
  }

  async guestLogin(): Promise<AuthResponse> {
    try {
      console.log('Attempting guest login...');
      const response = await api.post<AuthResponse>(API_ROUTES.users.guestLogin);
      
      const authData = response.data;
      if (!authData.access_token) {
        throw new Error('No access token in response');
      }
      
      this.setAuthToken(authData.access_token);
      return authData;
    } catch (error: any) {
      console.error('Guest login error:', error.response || error);
      if (error.response?.data?.detail) {
        throw new Error(error.response.data.detail);
      }
      throw new Error('Guest login failed: ' + (error.message || 'Unknown error'));
    }
  }

  async getCurrentUser(): Promise<UserResponse | null> {
    try {
      const response = await api.get<UserResponse>(API_ROUTES.users.me);
      return response.data;
    } catch (error) {
      console.error('Get current user error:', error);
      return null;
    }
  }

  async updateProfile(data: UserUpdate): Promise<UserResponse> {
    try {
      const response = await api.put<UserResponse>(API_ROUTES.users.me, data);
      return response.data;
    } catch (error: any) {
      console.error('Update profile error:', error.response || error);
      if (error.response?.data?.detail) {
        throw new Error(error.response.data.detail);
      }
      throw new Error('Failed to update profile');
    }
  }

  setAuthToken(token: string): void {
    localStorage.setItem('token', token);
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  }

  logout(): void {
    localStorage.removeItem('token');
    delete api.defaults.headers.common['Authorization'];
  }

  isAuthenticated(): boolean {
    return !!localStorage.getItem('token');
  }
}

// Add axios interceptor for handling 401 errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear invalid auth state
      const authService = new AuthService();
      authService.logout();
      
      // Redirect to login page
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Add request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log('Request:', {
      method: config.method,
      url: config.url,
      headers: config.headers,
      data: config.data
    });
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

export default new AuthService();
