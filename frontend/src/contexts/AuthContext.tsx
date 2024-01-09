import React, { createContext, useContext, useState, useEffect } from 'react';
import authService from '../services/authService';
import { UserResponse, UserCreate, UserLogin, AuthResponse } from '../types/api';
import LoadingSpinner from '../components/common/LoadingSpinner';

interface AuthContextType {
  user: UserResponse | null;
  setUser: React.Dispatch<React.SetStateAction<UserResponse | null>>;
  isAuthenticated: boolean;
  register: (data: UserCreate) => Promise<UserResponse>;
  login: (data: UserLogin) => Promise<void>;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const token = localStorage.getItem('token');
        if (token) {
          // Set the token in axios headers
          authService.setAuthToken(token);
          
          // Fetch current user data
          const currentUser = await authService.getCurrentUser();
          if (currentUser) {
            setUser(currentUser);
          }
        }
      } catch (error) {
        console.error('Failed to initialize auth:', error);
        // Clear potentially invalid token
        authService.logout();
      } finally {
        setLoading(false);
      }
    };

    initializeAuth();
  }, []);

  const register = async (data: UserCreate): Promise<UserResponse> => {
    const response = await authService.register(data);
    return response;
  };

  const login = async (data: UserLogin): Promise<void> => {
    try {
      const response = await authService.login(data);
      if (response.user) {
        setUser(response.user);
      } else {
        throw new Error('No user data in response');
      }
    } catch (error) {
      console.error('Login error in context:', error);
      throw error;
    }
  };

  const logout = () => {
    authService.logout();
    setUser(null);
  };

  const value = {
    user,
    setUser,
    isAuthenticated: !!user,
    register,
    login,
    logout,
    loading
  };

  if (loading) {
    return <LoadingSpinner fullScreen />;
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
