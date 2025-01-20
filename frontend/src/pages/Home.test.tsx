import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import { createTheme } from '@mui/material';
import Home from './Home';
import { createOrder } from '../services/orderService';
import { SnackbarProvider } from '../contexts/SnackbarContext';

// Mock the services and hooks
jest.mock('../services/orderService');
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate
}));

// Mock auth context with automatic guest login
const mockGuestLogin = jest.fn();
const mockSetUser = jest.fn();
const mockAuthResponse = {
  access_token: 'test-token',
  user: {
    id: 1,
    username: 'guest',
    email: 'guest@example.com',
    is_guest: true
  }
};

jest.mock('../contexts/AuthContext', () => ({
  ...jest.requireActual('../contexts/AuthContext'),
  useAuth: () => ({
    guestLogin: mockGuestLogin,
    user: null,
    setUser: mockSetUser
  })
}));

const theme = createTheme({
  components: {
    MuiSnackbar: {
      styleOverrides: {
        root: {
          '& .MuiPaper-root': {
            backgroundColor: '#fff',
          },
        },
      },
    },
  },
});

describe('Home Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Set up successful guest login response
    mockGuestLogin.mockResolvedValue(mockAuthResponse);
    (createOrder as jest.Mock).mockResolvedValue({
      order_number: 'TEST123',
      id: 1,
      customer_name: 'Test Customer',
      table_number: 1,
      user_id: 1,
      status: 'pending',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z'
    });
  });

  const renderComponent = () => {
    return render(
      <BrowserRouter>
        <ThemeProvider theme={theme}>
          <SnackbarProvider>
            <Home />
          </SnackbarProvider>
        </ThemeProvider>
      </BrowserRouter>
    );
  };

  it('should render welcome message and table number', () => {
    renderComponent();
    expect(screen.getByText(/Welcome to Our Restaurant/i)).toBeInTheDocument();
    expect(screen.getByText(/Table No:/i)).toBeInTheDocument();
  });

  it('should show error when submitting without customer name', async () => {
    renderComponent();
    const startButton = screen.getByText('Start Order');
    fireEvent.click(startButton);
    
    await waitFor(() => {
      expect(screen.getByText('Please enter customer name')).toBeInTheDocument();
    });
  });

  it('should automatically handle guest login and create order', async () => {
    renderComponent();
    
    // Fill in customer name
    const nameInput = screen.getByPlaceholderText('Enter customer name');
    fireEvent.change(nameInput, { target: { value: 'Test Customer' } });
    
    // Select order type
    const individualRadio = screen.getByLabelText('Individual Order');
    fireEvent.click(individualRadio);
    
    // Click start order
    const startButton = screen.getByText('Start Order');
    fireEvent.click(startButton);
    
    await waitFor(() => {
      // Verify guest login was called first
      expect(mockGuestLogin).toHaveBeenCalled();
      // Verify order was created with correct data
      expect(createOrder).toHaveBeenCalledWith({
        customer_name: 'Test Customer',
        is_group_order: false
      });
      // Verify navigation to menu page
      expect(mockNavigate).toHaveBeenCalledWith('/menu');
    });
  });

  it('should handle order creation failure gracefully', async () => {
    (createOrder as jest.Mock).mockRejectedValueOnce(new Error('Failed to create order'));
    renderComponent();
    
    const nameInput = screen.getByPlaceholderText('Enter customer name');
    fireEvent.change(nameInput, { target: { value: 'Test Customer' } });
    
    const startButton = screen.getByText('Start Order');
    fireEvent.click(startButton);
    
    await waitFor(() => {
      // Verify guest login was still successful
      expect(mockGuestLogin).toHaveBeenCalled();
      // Verify error message is shown
      expect(screen.getByText(/Failed to start order/i)).toBeInTheDocument();
    });
  });
}); 