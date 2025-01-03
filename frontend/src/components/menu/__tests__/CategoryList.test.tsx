import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { CategoryList } from '../CategoryList';
import { server } from '../../../mocks/server';
import { rest } from 'msw';

describe('CategoryList', () => {
  beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
  afterEach(() => {
    server.resetHandlers();
    jest.clearAllMocks();
  });
  afterAll(() => server.close());

  it('renders category list and performs CRUD operations', async () => {
    render(<CategoryList />);

    // Wait for initial categories to load
    await waitFor(() => {
      expect(screen.getByText('Main Course')).toBeInTheDocument();
    });

    // Test creating a new category
    const addButton = screen.getByText('Add Category');
    await act(async () => {
      fireEvent.click(addButton);
    });
    
    await waitFor(() => {
      expect(screen.getByRole('dialog')).toBeInTheDocument();
    });

    const nameInput = screen.getByLabelText('Name *');
    const descInput = screen.getByLabelText('Description');
    
    await act(async () => {
      await userEvent.type(nameInput, 'Desserts');
      await userEvent.type(descInput, 'Sweet treats');
    });
    
    const createButton = screen.getByRole('button', { name: /create/i });
    await waitFor(() => {
      expect(createButton).toBeEnabled();
    });

    await act(async () => {
      fireEvent.click(createButton);
    });

    // Wait for dialog to close
    await waitFor(() => {
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    });

    // Verify new category is added
    await waitFor(() => {
      expect(screen.getByText('Desserts')).toBeInTheDocument();
      expect(screen.getByText('Sweet treats')).toBeInTheDocument();
    }, { timeout: 3000 });

    // Test editing a category
    const editButtons = screen.getAllByLabelText(/edit/i);
    const editButton = editButtons[editButtons.length - 1]; // Get the last edit button (for Desserts)
    await act(async () => {
      fireEvent.click(editButton);
    });

    await waitFor(() => {
      expect(screen.getByRole('dialog')).toBeInTheDocument();
    });

    const editNameInput = screen.getByLabelText('Name *');
    const editDescInput = screen.getByLabelText('Description');

    await act(async () => {
      await userEvent.clear(editNameInput);
      await userEvent.clear(editDescInput);
      await userEvent.type(editNameInput, 'Desserts & Sweets');
      await userEvent.type(editDescInput, 'Delicious desserts');
    });
    
    const updateButton = screen.getByRole('button', { name: /update/i });
    await waitFor(() => {
      expect(updateButton).toBeEnabled();
    });

    await act(async () => {
      fireEvent.click(updateButton);
    });

    // Wait for dialog to close
    await waitFor(() => {
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    });

    // Verify category is updated
    await waitFor(() => {
      expect(screen.getByText('Desserts & Sweets')).toBeInTheDocument();
      expect(screen.getByText('Delicious desserts')).toBeInTheDocument();
    }, { timeout: 3000 });

    // Test toggling active status
    const toggleSwitches = screen.getAllByRole('checkbox', { name: /Toggle .* active status/i });
    const toggleSwitch = toggleSwitches[toggleSwitches.length - 1]; // Get the last toggle switch (for Desserts & Sweets)
    await act(async () => {
      fireEvent.click(toggleSwitch);
    });

    // Test deleting a category
    const deleteButtons = screen.getAllByLabelText(/delete/i);
    const deleteButton = deleteButtons[deleteButtons.length - 1]; // Get the last delete button (for Desserts & Sweets)
    window.confirm = jest.fn(() => true); // Mock confirm dialog
    await act(async () => {
      fireEvent.click(deleteButton);
    });

    // Verify category is deleted
    await waitFor(() => {
      expect(screen.queryByText('Desserts & Sweets')).not.toBeInTheDocument();
    }, { timeout: 3000 });
  }, 10000); // Increase test timeout

  it('handles error when creating category without name', async () => {
    render(<CategoryList />);

    await waitFor(() => {
      expect(screen.getByText('Add Category')).toBeInTheDocument();
    });

    // Try to create category without name
    await act(async () => {
      fireEvent.click(screen.getByText('Add Category'));
    });

    await waitFor(() => {
      expect(screen.getByRole('dialog')).toBeInTheDocument();
    });

    const createButton = screen.getByRole('button', { name: /create/i });
    await act(async () => {
      fireEvent.click(createButton);
    });

    // Verify error handling
    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent('Name is required');
    });
  });

  it('handles server error when loading categories', async () => {
    // Mock server error
    server.use(
      rest.get('http://localhost:8000/menu/categories/', (_, res, ctx) => {
        return res(ctx.status(500));
      })
    );

    render(<CategoryList />);

    // Verify error handling
    await waitFor(() => {
      expect(screen.getByText('Failed to load categories. Please try again.')).toBeInTheDocument();
    });
  });
});