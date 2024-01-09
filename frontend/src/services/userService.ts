import axios from 'axios';
import { User, UserCreate, UserUpdate, UserLoginCredentials, UserLoginResponse } from '../types/user';
import { handleApiError } from '../utils/errorHandler';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

class UserService {
  async getUsers(activeOnly: boolean = true): Promise<User[]> {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/users`, {
        params: { active_only: activeOnly }
      });
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  }

  async getUser(id: number): Promise<User> {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/users/${id}`);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  }

  async createUser(data: UserCreate): Promise<User> {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/users`, data);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  }

  async updateUser(id: number, data: UserUpdate): Promise<User> {
    try {
      const response = await axios.patch(`${API_BASE_URL}/api/users/${id}`, data);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  }

  async deleteUser(id: number): Promise<void> {
    try {
      await axios.delete(`${API_BASE_URL}/api/users/${id}`);
    } catch (error) {
      throw handleApiError(error);
    }
  }

  async login(credentials: UserLoginCredentials): Promise<UserLoginResponse> {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/auth/login`, credentials);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  }

  async logout(): Promise<void> {
    try {
      await axios.post(`${API_BASE_URL}/api/auth/logout`);
      // Clear local storage or any other client-side storage
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    } catch (error) {
      throw handleApiError(error);
    }
  }
}

export const userService = new UserService();
