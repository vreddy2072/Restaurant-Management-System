import axios from 'axios';

// In production, use relative path which will be handled by Vercel rewrites
// In development, use the full localhost URL
const isDevelopment = import.meta.env.MODE === 'development';
const API_URL = isDevelopment ? 'http://localhost:8000' : '';

console.log('API Service initialized with:', {
  environment: import.meta.env.MODE,
  apiUrl: API_URL
});

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Access-Control-Allow-Origin': 'http://localhost:5174',
    'Access-Control-Allow-Credentials': 'true'
  },
  withCredentials: true,
  xsrfCookieName: 'csrftoken',
  xsrfHeaderName: 'X-CSRFToken',
  validateStatus: (status) => {
    return status >= 200 && status < 500;
  }
});

// Add request interceptor to handle auth token and logging
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Add CORS headers
    config.headers['Access-Control-Allow-Origin'] = 'http://localhost:5174';
    config.headers['Access-Control-Allow-Credentials'] = 'true';
    
    // Log request details in development
    if (isDevelopment) {
      console.log(`Making ${config.method?.toUpperCase()} request to: ${config.url}`, {
        headers: config.headers,
        params: config.params,
        data: config.data
      });
    }
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
    // Log response details in development
    if (isDevelopment) {
      console.log(`Response from ${response.config.url}:`, {
        status: response.status,
        data: response.data
      });
    }
    return response;
  },
  async (error) => {
    // Log error details
    console.error(`API Error for ${error.config?.url}:`, {
      status: error.response?.status,
      data: error.response?.data,
      error: error.message
    });
    
    if (error.response?.status === 401) {
      // Clear token and redirect to login on authentication error
      localStorage.removeItem('token');
      delete api.defaults.headers.common['Authorization'];
      window.location.href = '/login';
    }

    // Retry the request if it failed due to network error
    if (!error.response && error.request && !error.config._retry) {
      error.config._retry = true;
      return api(error.config);
    }

    return Promise.reject(error);
  }
);

// Health check function
export const checkHealth = async () => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    console.error('Health check failed:', error);
    throw error;
  }
}; 