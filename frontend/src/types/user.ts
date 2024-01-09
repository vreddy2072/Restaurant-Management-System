export type UserRole = 'admin' | 'manager' | 'staff' | 'customer';

export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: UserRole;
  is_active: boolean;
  phone_number?: string;
  created_at: string;
  updated_at: string;
}

export interface UserCreate {
  username: string;
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  role: UserRole;
  is_active?: boolean;
  phone_number?: string;
}

export interface UserUpdate extends Partial<Omit<UserCreate, 'password'>> {
  id?: never;
  password?: string;
}

export interface UserLoginCredentials {
  email: string;
  password: string;
}

export interface UserLoginResponse {
  token: string;
  user: User;
}
