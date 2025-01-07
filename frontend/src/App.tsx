import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from 'react-router-dom';
import { AppBar, Toolbar, Typography, Container, Box, Button, Badge } from '@mui/material';
import { ShoppingCart as ShoppingCartIcon } from '@mui/icons-material';
import { MenuManagement } from './pages/MenuManagement';
import Menu from './pages/Menu';
import RegisterForm from './components/auth/RegisterForm';
import LoginForm from './components/auth/LoginForm';
import ProtectedRoute from './components/auth/ProtectedRoute';
import { useAuth } from './contexts/AuthContext';
import { CartProvider, useCart } from './contexts/CartContext';
import { SnackbarProvider } from './contexts/SnackbarContext';
import Cart from './components/cart/Cart';
import { AuthProvider } from './contexts/AuthContext';

function NavBar() {
  const navigate = useNavigate();
  const { isAuthenticated, logout, user } = useAuth();
  const { cart } = useCart();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const itemCount = cart?.items.reduce((total, item) => total + item.quantity, 0) || 0;

  return (
    <AppBar position="static" sx={{ minHeight: 56 }}>
      <Toolbar variant="dense" sx={{ minHeight: 56 }}>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Flavor Fusion Restaurant
        </Typography>
        {isAuthenticated ? (
          <>
            <Button color="inherit" component={Link} to="/" size="small">
              Menu
            </Button>

            <Button 
              color="inherit" 
              component={Link} 
              to="/cart" 
              size="small" 
              startIcon={
                <Badge badgeContent={itemCount} color="error">
                  <ShoppingCartIcon />
                </Badge>
              }
              sx={{ mx: 1 }}
            >
              Cart
            </Button>
            <Button color="inherit" component={Link} to="/admin/menu" size="small">
              Manage Menu
            </Button>            
            <Button color="inherit" onClick={handleLogout} size="small">
              Logout
            </Button>
          </>
        ) : (
          <>
            <Button color="inherit" component={Link} to="/login" size="small">
              Login
            </Button>
            <Button color="inherit" component={Link} to="/register" size="small" sx={{ ml: 1 }}>
              Register
            </Button>
          </>
        )}
      </Toolbar>
    </AppBar>
  );
}

function App() {
  return (
    <Router>
      <SnackbarProvider>
        <AuthProvider>
          <CartProvider>
            <Box sx={{ 
              minHeight: '100vh',
              bgcolor: 'background.default',
              display: 'flex',
              flexDirection: 'column'
            }}>
              <NavBar />
              <Box 
                component="main" 
                sx={{ 
                  flex: 1,
                  overflowY: 'auto',
                  pt: 4,
                  pb: 4
                }}
              >
                <Container>
                  <Routes>
                    <Route path="/register" element={<RegisterForm />} />
                    <Route path="/login" element={<LoginForm />} />
                    <Route
                      path="/cart"
                      element={
                        <ProtectedRoute>
                          <Cart />
                        </ProtectedRoute>
                      }
                    />
                    <Route
                      path="/admin/menu"
                      element={
                        <ProtectedRoute>
                          <MenuManagement />
                        </ProtectedRoute>
                      }
                    />                  
                    <Route
                      path="/"
                      element={
                        <ProtectedRoute>
                          <Menu />
                        </ProtectedRoute>
                      }
                    />
                  </Routes>
                </Container>
              </Box>
            </Box>
          </CartProvider>
        </AuthProvider>
      </SnackbarProvider>
    </Router>
  );
}

export default App;
