import type { Meta, StoryObj } from '@storybook/react';
import MenuItemCard from './MenuItemCard';

const meta: Meta<typeof MenuItemCard> = {
  title: 'Menu/MenuItemCard',
  component: MenuItemCard,
  tags: ['autodocs'],
  argTypes: {
    onEdit: { action: 'edit clicked' },
    onDelete: { action: 'delete clicked' }
  }
};

export default meta;
type Story = StoryObj<typeof MenuItemCard>;

export const Default: Story = {
  args: {
    item: {
      id: 1,
      name: 'Margherita Pizza',
      description: 'Fresh tomatoes, mozzarella, basil',
      price: 12.99,
      category_id: 1,
      category: 'Pizza',
      is_active: true,
      is_available: true,
      is_vegetarian: true,
      is_vegan: false,
      is_gluten_free: false,
      spice_level: 0,
      preparation_time: 15,
      average_rating: 4.5,
      rating_count: 128,
      allergens: [],
      customization_options: {
        'Size': ['Small', 'Medium', 'Large'],
        'Extra Toppings': ['Mushrooms', 'Olives', 'Extra Cheese']
      },
      image_url: 'https://example.com/pizza.jpg',
      created_at: '2023-01-01T00:00:00Z',
      updated_at: '2023-01-01T00:00:00Z'
    },
  },
};

export const Vegetarian: Story = {
  args: {
    item: {
      ...Default.args.item,
      id: 2,
      name: 'Veggie Delight Burger',
      description: 'Plant-based patty with fresh vegetables and vegan sauce',
      is_vegetarian: true,
      is_vegan: true,
      allergens: ['soy'],
      image_url: 'https://example.com/veggie-burger.jpg'
    }
  }
};

export const Loading: Story = {
  args: {
    isLoading: true,
    item: Default.args.item
  }
};

export const WithError: Story = {
  args: {
    item: Default.args.item,
    error: 'Failed to load image'
  }
};