// Generated from backend schemas
export interface UserBase {
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: 'admin' | 'staff' | 'customer';
  phone_number?: string;
}

export interface UserCreate extends UserBase {
  password: string;
}

export interface UserUpdate {
  first_name?: string;
  last_name?: string;
  phone_number?: string;
  password?: string;
  email?: string;
}

export interface UserResponse extends UserBase {
  id: number;
  is_active: boolean;
  is_guest: boolean;
  is_admin: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserLogin {
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: UserResponse;
}
