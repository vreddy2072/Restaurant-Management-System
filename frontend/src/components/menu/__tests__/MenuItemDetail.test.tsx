import { screen, fireEvent, waitFor } from '@testing-library/react';
import { render } from '../../../test-utils';
import { MenuItemDetail } from '../MenuItemDetail.tsx';
import { MenuItem } from '../../../types/menu';

const mockMenuItem: MenuItem = {
  id: 1,
  name: "Veggie Supreme Pizza",
  description: "Fresh vegetarian pizza with assorted toppings",
  price: 14.99,
  category_id: 1,
  is_vegetarian: true,
  is_vegan: false,
  is_gluten_free: false,
  spice_level: 1,
  preparation_time: 20,
  average_rating: 4.5,
  rating_count: 10,
  is_active: true,
  allergens: ["gluten", "dairy"],
  customization_options: {
    "Size": ["Small", "Medium", "Large"],
    "Crust": ["Thin", "Regular", "Thick"]
  },
  created_at: "2024-01-02T12:00:00",
  updated_at: "2024-01-02T12:00:00"
};

describe('MenuItemDetail', () => {
  it('renders menu item details correctly', async () => {
    render(<MenuItemDetail menuItem={mockMenuItem} />);

    // Basic information
    expect(screen.getByText('Veggie Supreme Pizza')).toBeInTheDocument();
    expect(screen.getByText('Fresh vegetarian pizza with assorted toppings')).toBeInTheDocument();
    expect(screen.getByText('$14.99')).toBeInTheDocument();
    expect(screen.getByText('20 mins preparation time')).toBeInTheDocument();

    // Dietary preferences
    expect(screen.getByTestId('vegetarian-icon')).toBeInTheDocument();
    expect(screen.queryByTestId('vegan-icon')).not.toBeInTheDocument();
    expect(screen.queryByTestId('gluten-free-icon')).not.toBeInTheDocument();
    
    // Spice level
    expect(screen.getByTestId('spice-level-1')).toBeInTheDocument();

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