export interface CartItem {
  id: number;
  menu_item_id: number;
  quantity: number;
  customization_choices?: { [key: string]: string };
  unit_price: number;
  subtotal: number;
  menu_item: {
    name: string;
    description: string;
    image_url?: string;
    price: number;
    customization_options?: { [key: string]: string[] };
  };
}

export interface Cart {
  id: number;
  user_id: number;
  items: CartItem[];
  total: number;
  created_at: string;
  updated_at: string;
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
