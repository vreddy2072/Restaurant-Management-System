import { rest } from 'msw';
import { API_URL, API_ROUTES } from '../constants/api';

export const handlers = [
  // Categories
  rest.get(`${API_URL}${API_ROUTES.menu.categories}`, (_, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json([
        {
          id: 1,
          name: 'Main Course',
          is_active: true,
        },
        {
          id: 2,
          name: 'Appetizers',
          is_active: true,
        },
      ])
    );
  }),

  // Menu Items
  rest.get(`${API_URL}${API_ROUTES.menu.items}`, (_, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json([
        {
          id: 1,
          name: 'Burger',
          description: 'Classic burger',
          price: 9.99,
          category_id: 1,
          is_active: true,
        },
      ])
    );
  }),

  rest.post(`${API_URL}${API_ROUTES.menu.items}`, (req, res, ctx) => {
    return res(
      ctx.status(201),
      ctx.json({
        id: 2,
        ...(req.body as object),
      })
    );
  }),

  rest.put(`${API_URL}${API_ROUTES.menu.items}/:id`, (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        id: Number(req.params.id),
        ...(req.body as object),
      })
    );
  }),

  rest.delete(`${API_URL}${API_ROUTES.menu.items}/:id`, (_, res, ctx) => {
    return res(ctx.status(204));
  }),
]; 