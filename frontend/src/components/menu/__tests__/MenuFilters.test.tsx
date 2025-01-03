import { screen, fireEvent, waitFor } from '@testing-library/react';
import { render } from '../../../test-utils';
import { MenuFilters } from '../MenuFilters.tsx';

describe('MenuFilters', () => {
  const mockOnFilterChange = jest.fn();

  beforeEach(() => {
    mockOnFilterChange.mockClear();
  });

  it('renders all filter sections correctly', () => {
    render(<MenuFilters onFilterChange={mockOnFilterChange} />);

    // Dietary preferences section
    expect(screen.getByText('Dietary Preferences')).toBeInTheDocument();
    expect(screen.getByLabelText('Vegetarian')).toBeInTheDocument();
    expect(screen.getByLabelText('Vegan')).toBeInTheDocument();
    expect(screen.getByLabelText('Gluten-Free')).toBeInTheDocument();

    // Price range section
    expect(screen.getByText('Price Range')).toBeInTheDocument();
    expect(screen.getByLabelText('Min Price')).toBeInTheDocument();
    expect(screen.getByLabelText('Max Price')).toBeInTheDocument();

    // Rating filter
    expect(screen.getByText('Minimum Rating')).toBeInTheDocument();
    expect(screen.getByTestId('rating-slider')).toBeInTheDocument();

    // Allergen filter section only shows when allergens are provided
    expect(screen.queryByText('Exclude Allergens')).not.toBeInTheDocument();
  });

  it('handles dietary preference changes', async () => {
    render(<MenuFilters onFilterChange={mockOnFilterChange} />);

    // Toggle dietary preferences
    fireEvent.click(screen.getByLabelText('Vegetarian'));
    expect(mockOnFilterChange).toHaveBeenCalledWith(expect.objectContaining({
      is_vegetarian: true
    }));

    fireEvent.click(screen.getByLabelText('Vegan'));
    expect(mockOnFilterChange).toHaveBeenCalledWith(expect.objectContaining({
      is_vegetarian: true,
      is_vegan: true
    }));

    fireEvent.click(screen.getByLabelText('Gluten-Free'));
    expect(mockOnFilterChange).toHaveBeenCalledWith(expect.objectContaining({
      is_vegetarian: true,
      is_vegan: true,
      is_gluten_free: true
    }));
  });

  it('handles price range input', async () => {
    render(<MenuFilters onFilterChange={mockOnFilterChange} />);

    const minPriceInput = screen.getByLabelText('Min Price');
    const maxPriceInput = screen.getByLabelText('Max Price');

    fireEvent.change(minPriceInput, { target: { value: '10' } });
    await waitFor(() => {
      expect(mockOnFilterChange).toHaveBeenCalledWith(expect.objectContaining({
        min_price: 10
      }));
    });

    fireEvent.change(maxPriceInput, { target: { value: '50' } });
    await waitFor(() => {
      expect(mockOnFilterChange).toHaveBeenCalledWith(expect.objectContaining({
        min_price: 10,
        max_price: 50
      }));
    });
  });

  it('handles rating filter changes', async () => {
    render(<MenuFilters onFilterChange={mockOnFilterChange} />);

    const ratingSlider = screen.getByTestId('rating-slider');
    fireEvent.mouseDown(ratingSlider);
    fireEvent.mouseMove(ratingSlider, { clientX: 200 }); // Move to roughly 4 on the scale
    fireEvent.mouseUp(ratingSlider);

    await waitFor(() => {
      expect(mockOnFilterChange).toHaveBeenCalledWith(expect.objectContaining({
        min_rating: expect.any(Number)
      }));
    });
  });

  it('handles allergen exclusion selection', async () => {
    const mockAllergens = ['dairy', 'nuts', 'gluten'];

    render(
      <MenuFilters 
        onFilterChange={mockOnFilterChange}
        availableAllergens={mockAllergens}
      />
    );

    expect(screen.getByText('Exclude Allergens')).toBeInTheDocument();
    const allergenSelect = screen.getByLabelText('Select allergens to exclude');
    fireEvent.mouseDown(allergenSelect);
    fireEvent.click(screen.getByText('Gluten'));
    fireEvent.click(screen.getByText('Dairy'));

    await waitFor(() => {
      expect(mockOnFilterChange).toHaveBeenCalledWith(expect.objectContaining({
        allergen_exclude_ids: [1, 2]
      }));
    });
  });

  it('provides a clear filters button', async () => {
    render(<MenuFilters onFilterChange={mockOnFilterChange} />);

    // Set some filters first
    fireEvent.click(screen.getByLabelText('Vegetarian'));
    fireEvent.change(screen.getByLabelText('Min Price'), { target: { value: '10' } });

    // Clear filters
    fireEvent.click(screen.getByText('Clear Filters'));

    await waitFor(() => {
      expect(mockOnFilterChange).toHaveBeenCalledWith({
        is_vegetarian: false,
        is_vegan: false,
        is_gluten_free: false,
        min_price: undefined,
        max_price: undefined,
        min_rating: undefined,
        allergen_exclude_ids: []
      });
    });
  });
}); 