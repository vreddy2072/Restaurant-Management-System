import axios from 'axios';

// In production, use relative path which will be handled by Vercel rewrites
// In development, use the full localhost URL
const isDevelopment = import.meta.env.VITE_NODE_ENV === 'development';
const baseURL = isDevelopment ? 'http://localhost:8000' : '';
const API_PREFIX = import.meta.env.VITE_API_URL || '/api';

console.log('API Service initialized with:', {
  environment: import.meta.env.VITE_NODE_ENV,
  baseURL,
  apiUrl: API_PREFIX
});

export const api = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: false
});

// Add request interceptor to handle auth token and logging
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    // Add API_PREFIX to URL in production
    if (!isDevelopment && !config.url?.startsWith(API_PREFIX)) {
      config.url = `${API_PREFIX}${config.url}`;
    }
    console.log(`Making ${config.method?.toUpperCase()} request to: ${config.url}`, {
      headers: config.headers,
      params: config.params,
      data: config.data
    });
    return config;
  },
  (error) => {
    console.error('Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling and logging
api.interceptors.response.use(
  (response) => {
    console.log(`Response from ${response.config.url}:`, {
      status: response.status,
      data: response.data
    });
    return response;
  },
  async (error) => {
    console.error(`API Error for ${error.config?.url}:`, {
      status: error.response?.status,
      data: error.response?.data,
      error: error.message
    });
    
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
    }
    return Promise.reject(error);
  }
);

// Health check function with logging
export const checkHealth = async () => {
  console.log('Checking API health...');
  try {
    const response = await api.get('/health');
    console.log('Health check response:', response.data);
    return response.data;
  } catch (error) {
    console.error('Health check failed:', error);
    throw error;
  }
}; 