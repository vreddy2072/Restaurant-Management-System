import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

interface CartSummaryProps {
  total: number;
}

const CartSummary: React.FC<CartSummaryProps> = ({ total = 0 }) => {
  const TAX_RATE = 0.08; // 8% tax rate
  const subtotal = total || 0;
  const tax = subtotal * TAX_RATE;
  const finalTotal = subtotal + tax;

  return (
    <Box sx={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'center', gap: 4 }}>
      <Box>
        <Box display="flex" alignItems="center" gap={2}>
          <Typography variant="body2" color="text.secondary">Subtotal:</Typography>
          <Typography variant="body2">${subtotal.toFixed(2)}</Typography>
        </Box>
        <Box display="flex" alignItems="center" gap={2}>
          <Typography variant="body2" color="text.secondary">Tax ({(TAX_RATE * 100).toFixed(0)}%):</Typography>
          <Typography variant="body2">${tax.toFixed(2)}</Typography>
        </Box>
      </Box>
      <Box display="flex" alignItems="center" gap={2}>
        <Typography variant="subtitle1" fontWeight="medium">Total:</Typography>
        <Typography variant="subtitle1" color="primary" fontWeight="medium">${finalTotal.toFixed(2)}</Typography>
      </Box>
    </Box>
  );
};

export default CartSummary;
