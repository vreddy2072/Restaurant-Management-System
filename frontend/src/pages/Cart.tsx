import React from 'react';
import { Box, Container } from '@mui/material';
import CartComponent from '../components/cart/Cart';

const CartPage: React.FC = () => {
  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'grey.50', py: 8 }}>
      <Container maxWidth="xl">
        <CartComponent />
      </Container>
    </Box>
  );
};

export default CartPage; 