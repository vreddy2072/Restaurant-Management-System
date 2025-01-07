import React, { useMemo, useState } from 'react';
import {
  Box,
  Typography,
  Button,
  CircularProgress,
  Paper,
  Divider,
  Container,
  Dialog,
  Alert,
} from '@mui/material';
import { useCart } from '../../contexts/CartContext';
import CartItem from './CartItem';
import CartSummary from './CartSummary';

const Cart: React.FC = () => {
  const { cart, loading, error, clearCart } = useCart();
  const [alertOpen, setAlertOpen] = useState(false);

  const cartTotal = useMemo(() => {
    if (!cart?.items) return 0;
    return cart.items.reduce((total, item) => {
      return total + (item.subtotal || 0);
    }, 0);
  }, [cart?.items]);

  const handleCheckout = () => {
    setAlertOpen(true);
  };

  const handleAlertClose = () => {
    setAlertOpen(false);
  };

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
              
              <Box>
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
              onClick={handleCheckout}
            >
              Proceed to Checkout
            </Button>
          </Box>
        </Container>
      </Paper>

      <Dialog
        open={alertOpen}
        onClose={handleAlertClose}
        PaperProps={{
          sx: {
            minWidth: '300px',
            maxWidth: '400px',
            m: 2
          }
        }}
      >
        <Alert 
          onClose={handleAlertClose} 
          severity="info" 
          variant="filled"
          sx={{ 
            fontSize: '1.1rem',
            padding: '16px 24px'
          }}
        >
          Checkout functionality is coming soon!
        </Alert>
      </Dialog>
    </Box>
  );
};

export default Cart;