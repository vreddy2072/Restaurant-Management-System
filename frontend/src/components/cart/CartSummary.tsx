import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

interface CartSummaryProps {
  total: number;
}

const CartSummary: React.FC<CartSummaryProps> = ({ total = 0 }) => {
  const TAX_RATE = 0.08; // 8% tax rate
  const subtotal = total;
  const tax = subtotal * TAX_RATE;
  const finalTotal = subtotal + tax;

  return (
    <Paper elevation={0} sx={{ p: 1, bgcolor: 'background.default' }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={0.5}>
        <Typography variant="body2">Subtotal:</Typography>
        <Typography variant="body2">${subtotal.toFixed(2)}</Typography>
      </Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={0.5}>
        <Typography variant="body2">Tax ({(TAX_RATE * 100).toFixed(0)}%):</Typography>
        <Typography variant="body2">${tax.toFixed(2)}</Typography>
      </Box>
      <Box display="flex" justifyContent="space-between" alignItems="center">
        <Typography variant="subtitle1" fontWeight="medium">Total:</Typography>
        <Typography variant="subtitle1" color="primary" fontWeight="medium">${finalTotal.toFixed(2)}</Typography>
      </Box>
    </Paper>
  );
};

export default CartSummary;
