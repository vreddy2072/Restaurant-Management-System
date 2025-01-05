import React from 'react';
import {
  Box,
  Typography,
  Button,
  CircularProgress,
  Paper,
  Divider,
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
    <Box p={2}>
      <Paper elevation={3}>
        <Box p={3}>
          <Typography variant="h5" gutterBottom>
            Your Cart
          </Typography>
          <Divider sx={{ my: 2 }} />
          
          {cart.items.map((item) => (
            <CartItem key={item.id} item={item} />
          ))}
          
          <Divider sx={{ my: 2 }} />
          <CartSummary total={cart.total} />
          
          <Box mt={3} display="flex" justifyContent="space-between">
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
            >
              Proceed to Checkout
            </Button>
          </Box>
        </Box>
      </Paper>
    </Box>
  );
};

export default Cart;
