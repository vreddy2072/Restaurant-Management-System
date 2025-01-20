import React, { useMemo } from 'react';
import {
  Box,
  Typography,
  Button,
  CircularProgress,
  Stack,
  Divider,
  Container,
  Modal,
  Alert,
  AlertTitle,
  Paper,
} from '@mui/material';
import { useCart } from '../../contexts/CartContext';
import CartItem from './CartItem';
import CartSummary from './CartSummary';

const Cart: React.FC = () => {
  const { cart, loading, error, clearCart } = useCart();
  const [isOpen, setIsOpen] = React.useState(false);

  const cartTotal = useMemo(() => {
    if (!cart?.cart_items) return 0;
    return cart.cart_items.reduce((total, item) => {
      return total + (item.menu_item.price * item.quantity);
    }, 0);
  }, [cart?.cart_items]);

  const handleCheckout = () => {
    setIsOpen(true);
  };

  const handleClose = () => {
    setIsOpen(false);
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" p={4}>
        <CircularProgress size={40} />
      </Box>
    );
  }

  if (error) {
    return (
      <Box p={4}>
        <Alert severity="error">
          <AlertTitle>Error</AlertTitle>
          {error}
        </Alert>
      </Box>
    );
  }

  if (!cart?.cart_items || cart.cart_items.length === 0) {
    return (
      <Box p={4}>
        <Typography variant="h5" align="center">
          Your cart is empty
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ pb: { xs: 16, sm: 14 } }}>
      <Container maxWidth="lg">
        <Box position="relative">
          <Paper elevation={2} sx={{ p: 4, borderRadius: 2 }}>
            <Typography variant="h4" sx={{ mb: 2 }}>
              Your Cart
            </Typography>
            <Divider sx={{ mb: 4 }} />
            
            <Stack spacing={4}>
              {cart.cart_items.map((item) => (
                <CartItem key={item.id} item={item} />
              ))}
            </Stack>
          </Paper>
        </Box>
      </Container>

      <Paper
        elevation={4}
        sx={{
          position: 'fixed',
          bottom: 0,
          left: 0,
          right: 0,
          zIndex: 1000,
          borderTop: 1,
          borderColor: 'divider'
        }}
      >
        <Container maxWidth="lg">
          <Stack
            direction={{ xs: 'column', sm: 'row' }}
            sx={{
              py: 3,
              px: 4,
              gap: 2,
              alignItems: 'center',
              justifyContent: 'space-between'
            }}
          >
            <Button
              variant="outlined"
              color="error"
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
              disabled={!cart?.cart_items || cart.cart_items.length === 0}
              size="medium"
              onClick={handleCheckout}
            >
              Confirm Order
            </Button>
          </Stack>
        </Container>
      </Paper>

      <Modal
        open={isOpen}
        onClose={handleClose}
        aria-labelledby="checkout-modal"
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}
      >
        <Paper sx={{ p: 4, mx: 2, maxWidth: 400 }}>
          <Alert severity="info">
            <AlertTitle>Coming Soon</AlertTitle>
            Checkout functionality is coming soon!
          </Alert>
        </Paper>
      </Modal>
    </Box>
  );
};

export default Cart;