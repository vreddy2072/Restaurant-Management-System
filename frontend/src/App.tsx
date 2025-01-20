import React from 'react';
import { HashRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import { createTheme } from '@mui/material';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import Home from './pages/Home';
import Menu from './pages/Menu';
import Cart from './pages/Cart';
import { MenuManagement } from './pages/MenuManagement';
import Unauthorized from './pages/Unauthorized';
import ReviewOrder from './pages/ReviewOrder';
import RateOrder from './pages/RateOrder';
import Navbar from './components/Navbar';
import ProtectedRoute from './components/auth/ProtectedRoute';
import { AuthProvider } from './contexts/AuthContext';
import { CartProvider } from './contexts/CartContext';
import { SnackbarProvider } from './contexts/SnackbarContext';
import OrderConfirmation from './pages/OrderConfirmation';

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

const App: React.FC = () => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <AuthProvider>
          <SnackbarProvider>
            <CartProvider>
              <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
                <Navbar />
                <Box component="main" sx={{ flexGrow: 1 }}>
                  <Routes>
                    <Route path="/" element={<Home />} />
                    <Route path="/menu" element={<Menu />} />
                    <Route path="/cart" element={<Cart />} />
                    <Route path="/unauthorized" element={<Unauthorized />} />
                    <Route path="/review-order" element={<ReviewOrder />} />
                    <Route path="/rate-order" element={<RateOrder />} />
                    <Route path="/order-confirmation/:orderNumber" element={<OrderConfirmation />} />
                    <Route
                      path="/admin/menu"
                      element={
                        <ProtectedRoute>
                          <MenuManagement />
                        </ProtectedRoute>
                      }
                    />
                  </Routes>
                </Box>
              </Box>
            </CartProvider>
          </SnackbarProvider>
        </AuthProvider>
      </Router>
    </ThemeProvider>
  );
};

export default App;
