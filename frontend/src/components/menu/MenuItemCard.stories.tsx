import type { Meta, StoryObj } from '@storybook/react';
import { MenuItemCard } from './MenuItemCard';

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
      name: 'Classic Burger',
      description: 'Juicy beef patty with fresh lettuce, tomatoes, and our special sauce',
      price: 12.99,
      category_id: 1,
      is_active: true,
      is_vegetarian: false,
      is_vegan: false,
      is_gluten_free: false,
      spice_level: 2,
      preparation_time: 15,
      average_rating: 4.5,
      rating_count: 128,
      allergens: ['dairy', 'gluten'],
      customization_options: {
        toppings: ['cheese', 'bacon', 'avocado'],
        sauces: ['special', 'bbq', 'ranch']
      },
      image_url: 'https://example.com/burger.jpg',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }
  }
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