import React from 'react';
import {
  Box,
  Typography,
  Button,
  CircularProgress,
  Paper,
  Divider,
  Container,
} from '@mui/material';
import { useCart } from '../../contexts/CartContext';
import CartItem from './CartItem';
import CartSummary from './CartSummary';

const Cart: React.FC = () => {
  const { cart, loading, error, clearCart } = useCart();

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" p={4}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box p={4}>
        <Typography color="error">{error}</Typography>
      </Box>
    );
  }

  if (!cart || cart.items.length === 0) {
    return (
      <Box p={4}>
        <Typography variant="h6" align="center">
          Your cart is empty
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ pb: { xs: 32, sm: 28 } }}>
      <Container maxWidth="lg">
        <Box sx={{ position: 'relative' }}>
          <Paper elevation={3}>
            <Box p={3}>
              <Typography variant="h5" gutterBottom>
                Your Cart
              </Typography>
              <Divider sx={{ my: 2 }} />
              
              <Box sx={{ 
                maxHeight: 'calc(100vh - 450px)',
                overflowY: 'auto',
                '&::-webkit-scrollbar': {
                  width: '8px',
                },
                '&::-webkit-scrollbar-track': {
                  backgroundColor: 'rgba(0,0,0,0.1)',
                  borderRadius: '4px',
                },
                '&::-webkit-scrollbar-thumb': {
                  backgroundColor: 'rgba(0,0,0,0.2)',
                  borderRadius: '4px',
                  '&:hover': {
                    backgroundColor: 'rgba(0,0,0,0.3)',
                  },
                },
              }}>
                {cart.items.map((item) => (
                  <CartItem key={item.id} item={item} />
                ))}
              </Box>
            </Box>
          </Paper>
        </Box>
      </Container>

      <Paper 
        elevation={3} 
        sx={{ 
          position: 'fixed', 
          bottom: 0, 
          left: 0, 
          right: 0, 
          zIndex: 1000,
          backgroundColor: 'background.paper',
          borderTop: 1,
          borderColor: 'divider',
        }}
      >
        <Container maxWidth="lg">
          <Box sx={{ p: 2 }}>
            <CartSummary total={cart.total} />
            <Divider sx={{ my: 2 }} />
            <Box 
              sx={{ 
                display: 'flex', 
                justifyContent: 'space-between',
                alignItems: 'center',
                gap: 2,
              }}
            >
              <Button
                variant="outlined"
                color="secondary"
                onClick={() => clearCart()}
              >
                Clear Cart
              </Button>
              <Button
                variant="contained"
                color="primary"
                disabled={cart.items.length === 0}
                size="large"
              >
                Proceed to Checkout
              </Button>
            </Box>
          </Box>
        </Container>
      </Paper>
    </Box>
  );
};

export default Cart;
