import { rest } from 'msw';

export const handlers = [
  // Categories
  rest.get('http://localhost:8000/menu/categories/', (_, res, ctx) => {
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
  rest.get('http://localhost:8000/menu/items/', (_, res, ctx) => {
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

  rest.post('http://localhost:8000/menu/items/', (req, res, ctx) => {
    return res(
      ctx.status(201),
      ctx.json({
        id: 2,
        ...(req.body as object),
      })
    );
  }),

  rest.put('http://localhost:8000/menu/items/:id', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        id: Number(req.params.id),
        ...(req.body as object),
      })
    );
  }),

  rest.delete('http://localhost:8000/menu/items/:id', (_, res, ctx) => {
    return res(ctx.status(204));
  }),
]; 