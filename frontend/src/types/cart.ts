export interface MenuItem {
  id: number;
  name: string;
  description: string;
  price: number;
  image_url?: string;
  customization_options?: { [key: string]: string[] };
}

export interface CartItem {
  id: number;
  menu_item_id: number;
  quantity: number;
  customizations?: { [key: string]: string };
  menu_item: MenuItem;
  created_at: string;
  updated_at: string;
}

export interface Cart {
  id: number;
  user_id: number;
  cart_items: CartItem[];
  order_number: string | null;
  created_at: string;
  updated_at?: string;
}

export interface AddToCartRequest {
  menu_item_id: number;
  quantity: number;
  customization_choices?: { [key: string]: string };
}

export interface UpdateCartItemRequest {
  quantity: number;
  customization_choices?: { [key: string]: string };
}

export interface CartTotal {
  subtotal: number;
  tax: number;
  total: number;
}
