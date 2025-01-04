import axios from 'axios';
import { API_ROUTES } from '../constants/api';
import {
  UserCreate,
  UserResponse,
  UserLogin,
  AuthResponse,
  UserUpdate
} from '../types/api';

// Configure axios defaults
const axiosInstance = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
});

class AuthService {
  async register(data: UserCreate): Promise<UserResponse> {
    try {
      console.log('Starting registration process...');
      console.log('Registration URL:', `${axiosInstance.defaults.baseURL}${API_ROUTES.users.register}`);
      console.log('Request headers:', axiosInstance.defaults.headers);
      console.log('Request data:', data);

      const response = await axiosInstance.request({
        method: 'POST',
        url: API_ROUTES.users.register,
        data,
        validateStatus: function (status) {
          console.log('Response status:', status);
          return status < 500; // Resolve only if the status code is less than 500
        }
      });

      console.log('Full response:', {
        status: response.status,
        statusText: response.statusText,
        headers: response.headers,
        data: response.data
      });

      if (response.status === 404) {
        throw new Error(`Endpoint not found: ${API_ROUTES.users.register}`);
      }

      if (response.status >= 400) {
        throw new Error(response.data?.detail || 'Registration failed');
      }

      return response.data;
    } catch (error: any) {
      console.error('Registration error details:', {
        error: error,
        response: error.response,
        message: error.message,
        stack: error.stack
      });

      if (error.response?.data?.detail) {
        throw new Error(error.response.data.detail);
      }
      throw error;
    }
  }

  async login(data: UserLogin): Promise<AuthResponse> {
    try {
      console.log('Login attempt with:', data);
      
      // Create form data
      const formData = new FormData();
      formData.append('email', data.email);  
      formData.append('password', data.password);
      
      const response = await axiosInstance.post<AuthResponse>(
        API_ROUTES.users.login, 
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      
      const authData = response.data;
      if (!authData.access_token) {
        throw new Error('No access token in response');
      }
      
      this.setAuthToken(authData.access_token);
      return authData;
    } catch (error: any) {
      console.error('Login error in service:', error.response || error);
      if (error.response?.data?.detail) {
        throw new Error(error.response.data.detail);
      }
      throw new Error('Login failed: ' + (error.message || 'Unknown error'));
    }
  }

  async getCurrentUser(): Promise<UserResponse | null> {
    try {
      const response = await axiosInstance.get<UserResponse>(API_ROUTES.users.me);
      return response.data;
    } catch (error) {
      console.error('Get current user error:', error);
      return null;
    }
  }

  async updateProfile(data: UserUpdate): Promise<UserResponse> {
    try {
      const response = await axiosInstance.put<UserResponse>(API_ROUTES.users.me, data);
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
    axiosInstance.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  }

  logout(): void {
    localStorage.removeItem('token');
    delete axiosInstance.defaults.headers.common['Authorization'];
  }

  isAuthenticated(): boolean {
    return !!localStorage.getItem('token');
  }
}

// Add axios interceptor for handling 401 errors
axiosInstance.interceptors.response.use(
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
axiosInstance.interceptors.request.use(
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
