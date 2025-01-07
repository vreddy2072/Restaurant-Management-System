import { screen, fireEvent, waitFor } from '@testing-library/react';
import { render } from '../../../test-utils';
import { MenuItemDetail } from '../MenuItemDetail.tsx';
import { MenuItem } from '../../../types/menu';

const mockMenuItem: MenuItem = {
  id: 1,
  name: 'Test Item',
  description: 'Test Description',
  price: 9.99,
  category_id: 1,
  category: { id: 1, name: 'Test Category' },
  is_vegetarian: true,
  is_vegan: false,
  is_gluten_free: false,
  is_available: true,
  spice_level: 2,
  preparation_time: 15,
  allergens: [],
  image_url: 'test.jpg',
  created_at: '2024-01-01',
  updated_at: '2024-01-01'
};

describe('MenuItemDetail', () => {
  it('renders menu item details correctly', async () => {
    render(<MenuItemDetail menuItem={mockMenuItem} />);

    // Basic information
    expect(screen.getByText('Test Item')).toBeInTheDocument();
    expect(screen.getByText('Test Description')).toBeInTheDocument();
    expect(screen.getByText('$9.99')).toBeInTheDocument();
    expect(screen.getByText('15 mins preparation time')).toBeInTheDocument();

    // Dietary preferences
    expect(screen.getByTestId('vegetarian-icon')).toBeInTheDocument();
    expect(screen.queryByTestId('vegan-icon')).not.toBeInTheDocument();
    expect(screen.queryByTestId('gluten-free-icon')).not.toBeInTheDocument();
    
    // Spice level
    expect(screen.getByTestId('spice-level-2')).toBeInTheDocument();

    // Rating
    expect(screen.getByRole('img', { name: '4.5 Stars' })).toBeInTheDocument();
    expect(screen.getByText('(10 reviews)')).toBeInTheDocument();
  });

  it('displays customization options correctly', async () => {
    render(<MenuItemDetail menuItem={mockMenuItem} />);

    // Customization section
    expect(screen.getByText('Customization Options')).toBeInTheDocument();
    
    // Size options
    const sizeLabel = screen.getByLabelText('Size');
    expect(sizeLabel).toBeInTheDocument();
    
    // Check if options are available in the select
    fireEvent.mouseDown(sizeLabel);
    expect(screen.getByText('Small')).toBeInTheDocument();
    expect(screen.getByText('Medium')).toBeInTheDocument();
    expect(screen.getByText('Large')).toBeInTheDocument();

    // Crust options
    const crustLabel = screen.getByLabelText('Crust');
    expect(crustLabel).toBeInTheDocument();
    
    // Check if options are available in the select
    fireEvent.mouseDown(crustLabel);
    expect(screen.getByText('Thin')).toBeInTheDocument();
    expect(screen.getByText('Regular')).toBeInTheDocument();
    expect(screen.getByText('Thick')).toBeInTheDocument();
  });

  it('handles customization selection', async () => {
    const onCustomizationChange = jest.fn();
    render(
      <MenuItemDetail 
        menuItem={mockMenuItem} 
        onCustomizationChange={onCustomizationChange}
      />
    );

    // Select size
    const sizeSelect = screen.getByLabelText('Size');
    fireEvent.mouseDown(sizeSelect);
    fireEvent.click(screen.getByText('Large'));

    // Select crust
    const crustSelect = screen.getByLabelText('Crust');
    fireEvent.mouseDown(crustSelect);
    fireEvent.click(screen.getByText('Thin'));

    expect(onCustomizationChange).toHaveBeenCalledWith({
      Size: 'Large',
      Crust: 'Thin'
    });
  });

  it('displays allergen warnings prominently', async () => {
    render(<MenuItemDetail menuItem={mockMenuItem} />);

    const allergenWarnings = screen.getByTestId('allergen-warnings');
    expect(allergenWarnings).toBeInTheDocument();
    expect(allergenWarnings).toHaveClass('MuiAlert-colorWarning');
    expect(screen.getByText(/Contains: Gluten, Dairy/)).toBeInTheDocument();
  });

  it('shows detailed dietary information on icon hover', async () => {
    render(<MenuItemDetail menuItem={mockMenuItem} />);

    const vegetarianIcon = screen.getByTestId('vegetarian-icon');
    fireEvent.mouseEnter(vegetarianIcon);

    await waitFor(() => {
      expect(screen.getByText('Suitable for vegetarians')).toBeInTheDocument();
    });
  });
}); 