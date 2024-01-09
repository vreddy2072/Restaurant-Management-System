export interface MenuItem {
  id: number;
  name: string;
  description: string;
  price: number;
  category_id: number;
  is_active: boolean;
  is_vegetarian: boolean;
  is_vegan: boolean;
  is_gluten_free: boolean;
  spice_level: number;
  preparation_time: number;
  average_rating: number;
  rating_count: number;
  allergens: string[];
  customization_options: {
    [key: string]: string[];
  };
  image_url?: string;
  created_at: string;
  updated_at: string;
}

export interface Category {
  id: number;
  name: string;
  description: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CategoryCreate extends Omit<Category, 'id' | 'created_at' | 'updated_at'> {
  name: string;
  description: string | null;
  is_active: boolean;
}

export interface CategoryUpdate extends Partial<CategoryCreate> {
  id?: never;
}

export interface MenuItemCreate extends Omit<MenuItem, 'id' | 'created_at' | 'updated_at'> {
  category_id: number;
}

export interface MenuItemUpdate extends Partial<MenuItemCreate> {
  id?: never;
}

export type Allergen = string; 