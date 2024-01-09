export const API_URL = 'http://localhost:8000';

// API routes should be relative since we're using axios baseURL
export const API_ROUTES = {
  users: {
    register: '/api/users/register',
    login: '/api/users/login',
    guestLogin: '/api/users/guest-login',
    me: '/api/users/me',
  },
  menu: {
    categories: '/api/menu/categories',
    items: '/api/menu/items',
  },
} as const;

// HTTP Status codes
export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  NOT_FOUND: 404,
  INTERNAL_SERVER_ERROR: 500,
} as const;
