import React, { useMemo } from 'react';
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

  const cartTotal = useMemo(() => {
    if (!cart?.items) return 0;
    return cart.items.reduce((total, item) => {
      return total + (item.subtotal || 0);
    }, 0);
  }, [cart?.items]);

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
    <Box sx={{ pb: { xs: 16, sm: 14 } }}>
      <Container maxWidth="lg">
        <Box sx={{ position: 'relative' }}>
          <Paper elevation={3}>
            <Box p={2}>
              <Typography variant="h5" gutterBottom>
                Your Cart
              </Typography>
              <Divider sx={{ my: 1 }} />
              
              <Box sx={{ 
                maxHeight: 'calc(100vh - 200px)',
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
          <Box 
            sx={{ 
              py: 1.5,
              px: 2,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              gap: 2
            }}
          >
            <Button
              variant="outlined"
              color="secondary"
              onClick={() => clearCart()}
              size="small"
            >
              Clear Cart
            </Button>

            <Box sx={{ flex: 1 }}>
              <CartSummary total={cartTotal} />
            </Box>

            <Button
              variant="contained"
              color="primary"
              disabled={cart.items.length === 0}
              size="medium"
            >
              Proceed to Checkout
            </Button>
          </Box>
        </Container>
      </Paper>
    </Box>
  );
};

export default Cart;