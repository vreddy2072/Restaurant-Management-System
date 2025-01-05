import React, { useState } from 'react';
import {
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Typography,
} from '@mui/material';
import { AddShoppingCart as AddShoppingCartIcon } from '@mui/icons-material';
import { MenuItem as MenuItemType } from '../../types/menu';
import { useCart } from '../../contexts/CartContext';

interface AddToCartButtonProps {
  menuItem: MenuItemType;
}

const AddToCartButton: React.FC<AddToCartButtonProps> = ({ menuItem }) => {
  const { addToCart } = useCart();
  const [open, setOpen] = useState(false);
  const [quantity, setQuantity] = useState(1);
  const [customization, setCustomization] = useState<{ [key: string]: string }>({});
  const [loading, setLoading] = useState(false);

  const handleOpen = () => setOpen(true);
  const handleClose = () => {
    setOpen(false);
    setQuantity(1);
    setCustomization({});
  };

  const handleAddToCart = async () => {
    try {
      setLoading(true);
      await addToCart({
        menu_item_id: menuItem.id,
        quantity,
        customization_choices: Object.keys(customization).length > 0 ? customization : undefined,
      });
      handleClose();
    } finally {
      setLoading(false);
    }
  };

  const handleCustomizationChange = (option: string, value: string) => {
    setCustomization(prev => ({
      ...prev,
      [option]: value,
    }));
  };

  return (
    <>
      <Button
        variant="contained"
        color="primary"
        startIcon={<AddShoppingCartIcon />}
        onClick={handleOpen}
        disabled={!menuItem.is_available}
        fullWidth
      >
        Add to Cart
      </Button>

      <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
        <DialogTitle>Add to Cart - {menuItem.name}</DialogTitle>
        <DialogContent>
          <Box sx={{ my: 2 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              {menuItem.description}
            </Typography>
            <Typography variant="h6" color="primary" gutterBottom>
              ${menuItem.price.toFixed(2)}
            </Typography>
          </Box>

          <TextField
            label="Quantity"
            type="number"
            value={quantity}
            onChange={(e) => setQuantity(Math.max(1, parseInt(e.target.value) || 1))}
            fullWidth
            margin="normal"
            InputProps={{ inputProps: { min: 1 } }}
          />

          {menuItem.customization_options && Object.entries(menuItem.customization_options).map(([option, choices]) => (
            <FormControl key={option} fullWidth margin="normal">
              <InputLabel>{option}</InputLabel>
              <Select
                value={customization[option] || ''}
                onChange={(e) => handleCustomizationChange(option, e.target.value)}
                label={option}
              >
                {choices.map((choice) => (
                  <MenuItem key={choice} value={choice}>
                    {choice}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          ))}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <Button
            onClick={handleAddToCart}
            variant="contained"
            color="primary"
            disabled={loading}
          >
            Add to Cart
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default AddToCartButton;
