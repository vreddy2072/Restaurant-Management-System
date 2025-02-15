import React, { useState } from 'react';
import {
  Box,
  Typography,
  IconButton,
  Card,
  CardContent,
  CardMedia,
  TextField,
  Chip,
} from '@mui/material';
import { Add as AddIcon, Remove as RemoveIcon, Delete as DeleteIcon } from '@mui/icons-material';
import { CartItem as CartItemType } from '../../types/cart';
import { useCart } from '../../contexts/CartContext';

interface CartItemProps {
  item: CartItemType;
}

const CartItem: React.FC<CartItemProps> = ({ item }) => {
  const { updateCartItem, removeFromCart } = useCart();
  const [loading, setLoading] = useState(false);

  const handleQuantityChange = async (newQuantity: number) => {
    if (newQuantity < 1) return;
    try {
      setLoading(true);
      await updateCartItem(item.id, {
        quantity: newQuantity,
        customization_choices: item.customization_choices,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleRemove = async () => {
    try {
      setLoading(true);
      await removeFromCart(item.id);
    } finally {
      setLoading(false);
    }
  };

  // If menu_item is missing, show a fallback UI
  if (!item.menu_item) {
    return (
      <Card sx={{ mb: 2, position: 'relative' }}>
        <CardContent>
          <Typography color="error">
            Item data unavailable
          </Typography>
          <Box display="flex" justifyContent="flex-end">
            <IconButton
              color="error"
              onClick={handleRemove}
              disabled={loading}
            >
              <DeleteIcon />
            </IconButton>
          </Box>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card sx={{ mb: 1, position: 'relative' }}>
      <Box display="flex">
        {item.menu_item.image_url && (
          <CardMedia
            component="img"
            sx={{ width: 100, height: 100, objectFit: 'cover' }}
            image={item.menu_item.image_url}
            alt={item.menu_item.name}
          />
        )}
        <CardContent sx={{ flex: 1, py: 1, px: 2, '&:last-child': { pb: 1 } }}>
          <Box display="flex" justifyContent="space-between" alignItems="flex-start">
            <Typography variant="subtitle1" sx={{ fontWeight: 'medium' }}>
              {item.menu_item.name}
            </Typography>
            <Typography variant="subtitle2" color="primary">
              ${(item.menu_item.price || 0).toFixed(2)}
            </Typography>
          </Box>

          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5, mb: 1 }}>
            {item.menu_item.description}
          </Typography>

          {item.customization_choices && Object.entries(item.customization_choices).length > 0 && (
            <Box sx={{ mb: 1 }}>
              {Object.entries(item.customization_choices).map(([key, value]) => (
                <Chip
                  key={key}
                  label={`${key}: ${value}`}
                  size="small"
                  sx={{ mr: 0.5, mb: 0.5 }}
                />
              ))}
            </Box>
          )}

          <Box display="flex" alignItems="center">
            <IconButton
              size="small"
              onClick={() => handleQuantityChange(item.quantity - 1)}
              disabled={loading || item.quantity <= 1}
            >
              <RemoveIcon fontSize="small" />
            </IconButton>
            <TextField
              size="small"
              value={item.quantity}
              InputProps={{ 
                readOnly: true,
                sx: { '& input': { py: 0.5, px: 0, textAlign: 'center' } }
              }}
              sx={{ width: 40, mx: 1 }}
            />
            <IconButton
              size="small"
              onClick={() => handleQuantityChange(item.quantity + 1)}
              disabled={loading}
            >
              <AddIcon fontSize="small" />
            </IconButton>

            <Box flex={1} />

            <Typography variant="subtitle2" sx={{ mx: 2 }}>
              ${(item.quantity * (item.menu_item.price || 0)).toFixed(2)}
            </Typography>

            <IconButton
              size="small"
              color="error"
              onClick={handleRemove}
              disabled={loading}
            >
              <DeleteIcon fontSize="small" />
            </IconButton>
          </Box>
        </CardContent>
      </Box>
    </Card>
  );
};

export default CartItem;
