import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '../../../contexts/AuthContext';
import LoginForm from '../LoginForm';

// Mock useNavigate
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
  Link: ({ children, to, ...props }: { children: React.ReactNode; to: string; [key: string]: any }) => (
    <a href={to} onClick={(e) => {
      e.preventDefault();
      mockNavigate(to);
    }} {...props}>{children}</a>
  ),
}));

// Mock auth service
jest.mock('../../../services/authService', () => ({
  __esModule: true,
  default: {
    login: jest.fn().mockResolvedValue({ user: { id: 1, email: 'test@example.com' }, access_token: 'token' }),
    guestLogin: jest.fn().mockResolvedValue({ user: { id: 2, email: 'guest@local' }, access_token: 'guest-token' }),
    setAuthToken: jest.fn(),
  },
}));

const renderLoginForm = () => {
  return render(
    <BrowserRouter>
      <AuthProvider>
        <LoginForm />
      </AuthProvider>
    </BrowserRouter>
  );
};

describe('LoginForm', () => {
  beforeEach(() => {
    mockNavigate.mockClear();
  });

  it('renders login form with all fields', () => {
    renderLoginForm();
    
    expect(screen.getByLabelText(/email address/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
  });

  it('shows validation errors for empty fields', async () => {
    renderLoginForm();
    
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    fireEvent.click(submitButton);

    const emailInput = screen.getByLabelText(/email address/i);
    const passwordInput = screen.getByLabelText(/password/i);

    expect(emailInput).toBeRequired();
    expect(passwordInput).toBeRequired();
  });

  it('handles successful login', async () => {
    renderLoginForm();
    
    const emailInput = screen.getByLabelText(/email address/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /sign in/i });

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/menu');
    });
  });

  it('shows error message on login failure', async () => {
    // Mock the login function to fail
    const authService = require('../../../services/authService').default;
    authService.login.mockRejectedValueOnce(new Error('Invalid credentials'));
    
    renderLoginForm();
    
    const emailInput = screen.getByLabelText(/email address/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /sign in/i });

    fireEvent.change(emailInput, { target: { value: 'wrong@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'wrongpassword' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/failed to sign in/i)).toBeInTheDocument();
    });
  });

  it('shows loading state while submitting', async () => {
    renderLoginForm();
    
    const emailInput = screen.getByLabelText(/email address/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /sign in/i });

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(submitButton);

    expect(submitButton).toBeDisabled();
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('navigates to registration page when clicking sign up link', () => {
    renderLoginForm();
    
    const signUpLink = screen.getByRole('link', { name: /don't have an account\? sign up/i });
    fireEvent.click(signUpLink);

    expect(mockNavigate).toHaveBeenCalledWith('/register');
  });

  it('renders guest login button', () => {
    renderLoginForm();
    
    expect(screen.getByRole('button', { name: /continue as guest/i })).toBeInTheDocument();
  });

  it('handles successful guest login', async () => {
    renderLoginForm();
    
    const guestButton = screen.getByRole('button', { name: /continue as guest/i });
    fireEvent.click(guestButton);

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/menu');
    });
  });

  it('shows error message on guest login failure', async () => {
    // Mock the guest login function to fail
    const authService = require('../../../services/authService').default;
    authService.guestLogin.mockRejectedValueOnce(new Error('Guest login failed'));
    
    renderLoginForm();
    
    const guestButton = screen.getByRole('button', { name: /continue as guest/i });
    fireEvent.click(guestButton);

    await waitFor(() => {
      expect(screen.getByText(/failed to sign in as guest/i)).toBeInTheDocument();
    });
  });

  it('disables both login and guest buttons while loading', async () => {
    renderLoginForm();
    
    const signInButton = screen.getByRole('button', { name: /sign in/i });
    const guestButton = screen.getByRole('button', { name: /continue as guest/i });
    
    fireEvent.click(guestButton);

    expect(signInButton).toBeDisabled();
    expect(guestButton).toBeDisabled();
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });
});
