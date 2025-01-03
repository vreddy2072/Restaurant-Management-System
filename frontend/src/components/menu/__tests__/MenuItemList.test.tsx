import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { act } from 'react';
import { MenuItemList } from '../MenuItemList';
import { menuService } from '../../../services/menuService';
import { MenuItem } from '../../../types/menu';

jest.mock('../../../services/menuService', () => ({
  menuService: {
    getMenuItems: jest.fn(),
    getCategories: jest.fn(),
    createMenuItem: jest.fn(),
    updateMenuItem: jest.fn(),
    deleteMenuItem: jest.fn(),
  },
}));

describe('MenuItemList', () => {
  const mockMenuItems: MenuItem[] = [
    {
      id: 1,
      name: 'Burger',
      description: 'Classic burger',
      price: 9.99,
      category_id: 1,
      is_active: true,
      is_vegetarian: false,
      is_vegan: false,
      is_gluten_free: false,
      spice_level: 0,
      preparation_time: 15,
      average_rating: 4.5,
      rating_count: 10,
      allergens: [],
      customization_options: {},
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
  ];

  const mockCategories = [
    {
      id: 1,
      name: 'Main Course',
      description: null,
      is_active: true,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
  ];

  const newMenuItem: MenuItem = {
    id: 2,
    name: 'Pizza',
    description: 'Delicious pizza',
    price: 12.99,
    category_id: 1,
    is_active: true,
    is_vegetarian: false,
    is_vegan: false,
    is_gluten_free: false,
    spice_level: 0,
    preparation_time: 15,
    average_rating: 0,
    rating_count: 0,
    allergens: [],
    customization_options: {},
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
    (menuService.getMenuItems as jest.Mock).mockResolvedValue(mockMenuItems);
    (menuService.getCategories as jest.Mock).mockResolvedValue(mockCategories);
    (menuService.createMenuItem as jest.Mock).mockImplementation(async (data) => ({
      id: 2,
      ...data,
      is_active: true,
      is_vegetarian: false,
      is_vegan: false,
      is_gluten_free: false,
      spice_level: 0,
      preparation_time: 15,
      average_rating: 0,
      rating_count: 0,
      allergens: [],
      customization_options: {},
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }));
    (menuService.updateMenuItem as jest.Mock).mockImplementation(async (id, data) => ({
      ...mockMenuItems.find(item => item.id === id),
      ...data,
      updated_at: new Date().toISOString(),
    }));
    (menuService.deleteMenuItem as jest.Mock).mockResolvedValue(undefined);

    // Mock window.confirm
    const confirmSpy = jest.spyOn(window, 'confirm');
    confirmSpy.mockImplementation(() => true);
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('renders menu items list and performs CRUD operations', async () => {
    await act(async () => {
      render(<MenuItemList />);
    });

    // Wait for initial data to load
    await waitFor(() => {
      expect(screen.getByText('Burger')).toBeInTheDocument();
    });

    // Add new menu item
    fireEvent.click(screen.getByText('Add Menu Item'));

    // Wait for dialog to open and form fields to be available
    await waitFor(() => {
      expect(screen.getByLabelText('Name')).toBeInTheDocument();
      expect(screen.getByLabelText('Description')).toBeInTheDocument();
      expect(screen.getByLabelText('Price')).toBeInTheDocument();
      expect(screen.getByLabelText('Category')).toBeInTheDocument();
    });

    // Fill in form fields
    await act(async () => {
      await userEvent.type(screen.getByLabelText('Name'), 'Pizza');
      await userEvent.type(screen.getByLabelText('Description'), 'Delicious pizza');
      await userEvent.type(screen.getByLabelText('Price'), '12.99');
      
      // Select category
      fireEvent.mouseDown(screen.getByLabelText('Category'));
    });

    // Wait for category options to be available
    await waitFor(() => {
      expect(screen.getAllByText('Main Course')[0]).toBeInTheDocument();
    });

    await act(async () => {
      const options = screen.getAllByText('Main Course');
      const menuItemOption = options.find(
        element => element.getAttribute('role') === 'option'
      );
      if (menuItemOption) {
        fireEvent.click(menuItemOption);
      }
    });

    // Update mock for getMenuItems to include the new item
    const updatedMenuItems = [...mockMenuItems, newMenuItem];
    (menuService.getMenuItems as jest.Mock).mockResolvedValue(updatedMenuItems);

    // Submit form
    await act(async () => {
      fireEvent.click(screen.getByText('Create'));
    });

    // Wait for dialog to close
    await waitFor(() => {
      expect(screen.queryByText('Create')).not.toBeInTheDocument();
    });

    // Verify new menu item is added
    await waitFor(() => {
      expect(screen.getByText('Pizza')).toBeInTheDocument();
      expect(screen.getByText('Delicious pizza')).toBeInTheDocument();
      expect(screen.getByText('$12.99')).toBeInTheDocument();
    }, { timeout: 5000 });

    // Edit menu item
    const editButtons = await screen.findAllByLabelText(/Edit/);
    await act(async () => {
      fireEvent.click(editButtons[0]);
    });

    await waitFor(() => {
      expect(screen.getByLabelText('Description')).toBeInTheDocument();
    });

    await act(async () => {
      await userEvent.clear(screen.getByLabelText('Description'));
      await userEvent.type(screen.getByLabelText('Description'), 'Updated burger');
    });

    // Update mock for getMenuItems to reflect the edit
    const editedMenuItems = updatedMenuItems.map(item =>
      item.id === 1 ? { ...item, description: 'Updated burger' } : item
    );
    (menuService.getMenuItems as jest.Mock).mockResolvedValue(editedMenuItems);

    await act(async () => {
      fireEvent.click(screen.getByText('Update'));
    });

    // Wait for dialog to close
    await waitFor(() => {
      expect(screen.queryByText('Update')).not.toBeInTheDocument();
    });

    // Verify menu item is updated
    await waitFor(() => {
      expect(screen.getByText('Updated burger')).toBeInTheDocument();
    });

    // Update mock for getMenuItems to reflect deletion before clicking delete
    (menuService.getMenuItems as jest.Mock).mockResolvedValue([newMenuItem]);

    // Delete menu item
    const deleteButtons = await screen.findAllByLabelText(/Delete/);
    await act(async () => {
      fireEvent.click(deleteButtons[0]);
    });

    // Wait for the delete operation to complete and verify the item is removed
    await waitFor(() => {
      expect(screen.queryByText('Burger')).not.toBeInTheDocument();
    });
  }, 10000);

  it('handles error when creating menu item without required fields', async () => {
    await act(async () => {
      render(<MenuItemList />);
    });

    fireEvent.click(screen.getByText('Add Menu Item'));

    await waitFor(() => {
      expect(screen.getByText('Create')).toBeInTheDocument();
    });

    await act(async () => {
      fireEvent.click(screen.getByText('Create'));
    });

    await waitFor(() => {
      expect(screen.getByText('Name is required')).toBeInTheDocument();
      expect(screen.getByText('Price must be greater than 0')).toBeInTheDocument();
    });
  });

  it('handles server error when loading menu items', async () => {
    (menuService.getMenuItems as jest.Mock).mockRejectedValueOnce(new Error('Failed to load data'));

    await act(async () => {
      render(<MenuItemList />);
    });

    await waitFor(() => {
      expect(screen.getByText('Failed to load data. Please try again.')).toBeInTheDocument();
    });
  });
}); 