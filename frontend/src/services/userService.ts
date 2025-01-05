import { api } from './api';
import { User, UserCreate, UserUpdate, UserLoginCredentials, UserLoginResponse } from '../types/user';
import { handleApiError } from '../utils/errorHandler';

class UserService {
  async getUsers(activeOnly: boolean = true): Promise<User[]> {
    try {
      const response = await api.get('/api/users', {
        params: { active_only: activeOnly }
      });
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  }

  async getUser(id: number): Promise<User> {
    try {
      const response = await api.get(`/api/users/${id}`);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  }

  async createUser(userData: UserCreate): Promise<User> {
    try {
      const response = await api.post('/api/users', userData);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  }

  async updateUser(id: number, userData: UserUpdate): Promise<User> {
    try {
      const response = await api.put(`/api/users/${id}`, userData);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  }

  async deleteUser(id: number): Promise<void> {
    try {
      await api.delete(`/api/users/${id}`);
    } catch (error) {
      throw handleApiError(error);
    }
  }

  async login(credentials: UserLoginCredentials): Promise<UserLoginResponse> {
    try {
      const response = await api.post('/api/auth/login', credentials);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  }

  async getCurrentUser(): Promise<User> {
    try {
      const response = await api.get('/api/users/me');
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  }
}

export const userService = new UserService();
