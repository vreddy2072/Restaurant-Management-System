import { api } from './api';

export interface User {
  id: number;
  email: string;
  username?: string;
  is_guest?: boolean;
  role?: string;
}

export interface GuestUserResponse {
  access_token: string;
  token_type: string;
  user: User;
  temp_password: string;
}

export const createGuestUser = async (): Promise<GuestUserResponse> => {
  try {
    const response = await api.post(`/api/users/guest-login`);
    const data = response.data;
    
    // Ensure the user object has the required fields
    if (!data.user || !data.access_token) {
      throw new Error('Invalid guest user response');
    }
    
    // Set the auth token in localStorage and api defaults
    localStorage.setItem('token', data.access_token);
    api.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`;
    
    return {
      access_token: data.access_token,
      token_type: data.token_type || 'bearer',
      user: {
        ...data.user,
        is_guest: true,
        role: 'guest'
      },
      temp_password: data.temp_password
    };
  } catch (error) {
    console.error('Error creating guest user:', error);
    throw error;
  }
};
