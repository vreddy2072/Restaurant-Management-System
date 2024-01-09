import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

interface CartSummaryProps {
  total: number;
}

const CartSummary: React.FC<CartSummaryProps> = ({ total }) => {
  const TAX_RATE = 0.08; // 8% tax rate
  const subtotal = total;
  const tax = subtotal * TAX_RATE;
  const finalTotal = subtotal + tax;

  return (
    <Paper elevation={0} sx={{ p: 2, bgcolor: 'background.default' }}>
      <Box display="flex" justifyContent="space-between" mb={1}>
        <Typography variant="body1">Subtotal:</Typography>
        <Typography variant="body1">${subtotal.toFixed(2)}</Typography>
      </Box>
      <Box display="flex" justifyContent="space-between" mb={1}>
        <Typography variant="body1">Tax ({(TAX_RATE * 100).toFixed(0)}%):</Typography>
        <Typography variant="body1">${tax.toFixed(2)}</Typography>
      </Box>
      <Box display="flex" justifyContent="space-between" mt={2}>
        <Typography variant="h6">Total:</Typography>
        <Typography variant="h6" color="primary">${finalTotal.toFixed(2)}</Typography>
      </Box>
    </Paper>
  );
};

export default CartSummary;
