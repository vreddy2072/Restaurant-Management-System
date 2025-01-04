import { setupServer } from 'msw/node';
import { rest } from 'msw';

const API_URL = 'http://localhost:8000';

// Mock data store
let categories = [
  {
    id: 1,
    name: 'Main Course',
    description: 'Main dishes',
    is_active: true,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
];

let menuItems = [
  {
    id: 1,
    name: 'Burger',
    description: 'Classic burger',
    price: 9.99,
    category_id: 1,
    is_active: true,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
];

interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

let users: User[] = [];

export const server = setupServer(
  // Auth endpoints
  rest.post(`${API_URL}/api/users/register`, async (req, res, ctx) => {
    const data = await req.json();
    if (!data.email || !data.password || !data.first_name || !data.last_name || !data.role) {
      return res(
        ctx.status(400),
        ctx.json({ detail: 'All fields are required' })
      );
    }

    const newUser = {
      id: users.length + 1,
      username: data.username,
      email: data.email,
      first_name: data.first_name,
      last_name: data.last_name,
      role: data.role,
      is_active: true,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };

    users.push(newUser);
    return res(ctx.status(201), ctx.json(newUser));
  }),

  rest.post(`${API_URL}/api/users/login`, async (req, res, ctx) => {
    const data = await req.json();
    if (!data.email || !data.password) {
      return res(
        ctx.status(400),
        ctx.json({ detail: 'Email and password are required' })
      );
    }

    const user = users.find(u => u.email === data.email);
    if (!user) {
      return res(
        ctx.status(401),
        ctx.json({ detail: 'Invalid credentials' })
      );
    }

    return res(ctx.json({
      access_token: 'mock_jwt_token',
      token_type: 'Bearer',
      user: user
    }));
  }),

  // Category endpoints
  rest.get(`${API_URL}/api/menu/categories/`, (req, res, ctx) => {
    const activeOnly = req.url.searchParams.get('active_only') === 'true';
    let filteredCategories = categories;
    if (activeOnly) {
      filteredCategories = categories.filter(c => c.is_active);
    }
    return res(ctx.json(filteredCategories));
  }),

  rest.post(`${API_URL}/api/menu/categories/`, async (req, res, ctx) => {
    const data = await req.json();
    if (!data.name) {
      return res(ctx.status(400), ctx.json({ detail: 'Name is required' }));
    }

    const newCategory = {
      id: categories.length + 1,
      name: data.name,
      description: data.description || '',
      is_active: true,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    categories.push(newCategory);
    return res(ctx.json(newCategory));
  }),

  rest.put(`${API_URL}/api/menu/categories/:id`, async (req, res, ctx) => {
    const { id } = req.params;
    const data = await req.json();
    const index = categories.findIndex(c => c.id === Number(id));
    
    if (index === -1) {
      return res(ctx.status(404), ctx.json({ detail: 'Category not found' }));
    }

    categories[index] = {
      ...categories[index],
      ...data,
      updated_at: new Date().toISOString(),
    };

    return res(ctx.json(categories[index]));
  }),

  rest.delete(`${API_URL}/api/menu/categories/:id`, (req, res, ctx) => {
    const { id } = req.params;
    categories = categories.filter(c => c.id !== Number(id));
    return res(ctx.status(204));
  }),

  // Menu item endpoints
  rest.get(`${API_URL}/api/menu/items/`, (req, res, ctx) => {
    const categoryId = req.url.searchParams.get('category_id');
    const activeOnly = req.url.searchParams.get('active_only') === 'true';
    
    let filteredItems = menuItems;
    if (categoryId) {
      filteredItems = filteredItems.filter(i => i.category_id === Number(categoryId));
    }
    if (activeOnly) {
      filteredItems = filteredItems.filter(i => i.is_active);
    }
    
    return res(ctx.json(filteredItems));
  }),

  rest.post(`${API_URL}/api/menu/items/`, async (req, res, ctx) => {
    const data = await req.json();
    if (!data.name || !data.price || !data.category_id) {
      return res(
        ctx.status(400),
        ctx.json({ detail: 'Name, price, and category_id are required' })
      );
    }

    const newItem = {
      id: menuItems.length + 1,
      name: data.name,
      description: data.description || '',
      price: data.price,
      category_id: data.category_id,
      is_active: true,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    menuItems.push(newItem);
    return res(ctx.json(newItem));
  }),

  rest.put(`${API_URL}/api/menu/items/:id`, async (req, res, ctx) => {
    const { id } = req.params;
    const data = await req.json();
    const index = menuItems.findIndex(i => i.id === Number(id));
    
    if (index === -1) {
      return res(ctx.status(404), ctx.json({ detail: 'Menu item not found' }));
    }

    menuItems[index] = {
      ...menuItems[index],
      ...data,
      updated_at: new Date().toISOString(),
    };

    return res(ctx.json(menuItems[index]));
  }),

  rest.delete(`${API_URL}/api/menu/items/:id`, (req, res, ctx) => {
    const { id } = req.params;
    menuItems = menuItems.filter(i => i.id !== Number(id));
    return res(ctx.status(204));
  }),
);