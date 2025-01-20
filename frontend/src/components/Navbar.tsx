import React, { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Button,
  Typography,
  Box,
  IconButton,
  Badge,
} from '@mui/material';
import ShoppingCartIcon from '@mui/icons-material/ShoppingCart';
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';
import { useAuth } from '../contexts/AuthContext';
import { useCart } from '../contexts/CartContext';

const Navbar: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated, logout, user } = useAuth();
  const { cart } = useCart();

  const cartItemCount = cart?.cart_items?.length || 0;

  // Add debugging for auth state changes
  useEffect(() => {
    console.log('Auth state changed:', { isAuthenticated, user, currentPath: location.pathname });
  }, [isAuthenticated, user, location.pathname]);

  const isActive = (path: string) => location.pathname === path;

  const handleLogout = async () => {
    try {
      console.log('Starting logout process...');
      await logout();
      console.log('Logout successful, navigating to home...');
      // Force a re-render before navigation
      setTimeout(() => {
        navigate('/', { replace: true });
      }, 0);
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  // Add debugging for render
  console.log('Navbar rendering:', { isAuthenticated, currentPath: location.pathname });

  return (
    <AppBar position="static">
      <Toolbar sx={{ display: 'flex', justifyContent: 'space-between' }}>
        {/* Left section */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Typography variant="h6" component="div" sx={{ mr: 4 }}>
            Restaurant
          </Typography>
          {isAuthenticated && (
            <>
              <Button
                color="inherit"
                onClick={() => navigate('/menu')}
                sx={{ 
                  backgroundColor: isActive('/menu') ? 'rgba(255, 255, 255, 0.1)' : 'transparent'
                }}
              >
                Menu
              </Button>
              <IconButton 
                color="inherit" 
                onClick={() => navigate('/cart')}
                sx={{ 
                  backgroundColor: isActive('/cart') ? 'rgba(255, 255, 255, 0.1)' : 'transparent'
                }}
              >
                <Badge badgeContent={cartItemCount} color="error">
                  <ShoppingCartIcon />
                </Badge>
              </IconButton>
            </>
          )}
          {!isAuthenticated && location.pathname !== '/' && (
            <Button
              color="inherit"
              onClick={() => navigate('/')}
              sx={{ 
                backgroundColor: isActive('/') ? 'rgba(255, 255, 255, 0.1)' : 'transparent'
              }}
            >
              Home
            </Button>
          )}
        </Box>

        {/* Center section */}
        {isAuthenticated && (
          <Box sx={{ display: 'flex', gap: 2, position: 'absolute', left: '50%', transform: 'translateX(-50%)' }}>
            <Button
              color="inherit"
              onClick={() => navigate('/review-order')}
              sx={{ 
                backgroundColor: isActive('/review-order') ? 'rgba(255, 255, 255, 0.1)' : 'transparent'
              }}
            >
              Review Order
            </Button>
            <Button
              color="inherit"
              onClick={() => navigate('/rate-order')}
              sx={{ 
                backgroundColor: isActive('/rate-order') ? 'rgba(255, 255, 255, 0.1)' : 'transparent'
              }}
            >
              Rate Order
            </Button>
          </Box>
        )}

        {/* Right section */}
        {isAuthenticated && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Button
              color="inherit"
              onClick={() => {
                console.log('Navigating to admin menu...');
                navigate('/admin/menu');
              }}
              startIcon={<AdminPanelSettingsIcon />}
              sx={{ 
                backgroundColor: isActive('/admin/menu') ? 'rgba(255, 255, 255, 0.1)' : 'transparent'
              }}
            >
              Admin
            </Button>
            <Button 
              color="inherit"
              onClick={handleLogout}
            >
              Logout
            </Button>
          </Box>
        )}
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;
