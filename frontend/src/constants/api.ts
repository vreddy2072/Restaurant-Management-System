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
    fullMenu: '/api/menu/full',
    filter: '/api/menu/items/filter',
    allergens: '/api/menu/allergens',
    rate: (itemId: number) => `/api/menu/items/${itemId}/rate`,
    customize: (itemId: number) => `/api/menu/items/${itemId}/customize`,
    uploadImage: (itemId: number) => `/api/menu/items/${itemId}/image`,
  },
  cart: {
    get: '/api/cart',
    clear: '/api/cart',
    getByOrder: (orderNumber: string) => `/api/cart/order/${orderNumber}`,
    addItem: '/api/cart/items',
    updateItem: (itemId: number) => `/api/cart/items/${itemId}`,
    removeItem: (itemId: number) => `/api/cart/items/${itemId}`,
    total: '/api/cart/total'
  },
  ratings: {
    menuItem: {
      rate: (menuItemId: number) => `/api/ratings/menu-items/${menuItemId}`,
      get: (menuItemId: number) => `/api/ratings/menu-items/${menuItemId}`,
      delete: (menuItemId: number) => `/api/ratings/menu-items/${menuItemId}`,
      getUserRating: (menuItemId: number) => `/api/ratings/menu-items/${menuItemId}/user`,
      getAverage: (menuItemId: number) => `/api/ratings/menu-items/${menuItemId}/average`,
    },
    restaurantFeedback: {
      create: '/api/ratings/restaurant-feedback',
      getAll: '/api/ratings/restaurant-feedback',
      getUserFeedback: '/api/ratings/restaurant-feedback/user',
      getStats: '/api/ratings/restaurant-feedback/stats',
      getRecent: '/api/ratings/restaurant-feedback/recent'
    }
  },
  orders: {
    create: '/api/orders/create',
    getById: (orderId: number) => `/api/orders/get_order_by_id/${orderId}`,
    getByNumber: (orderNumber: string) => `/api/orders/get_order_by_number/${orderNumber}`,
    getAll: '/api/orders/get_orders',
    update: (orderId: number) => `/api/orders/update_order/${orderId}`,
    cancel: (orderId: number) => `/api/orders/cancel_order/${orderId}`,
    confirm: (orderId: number) => `/api/orders/confirm_order/${orderId}`,
    getByStatus: (status: string) => `/api/orders/get_orders_by_status/${status}`
  }
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
