import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Switch,
  Box,
  Alert,
  Slider,
  Typography,
  Chip,
  Stack
} from '@mui/material';
import { MenuItem as MenuItemType, Category, MenuItemUpdate, MenuItemCreate } from '../../types/menu';
import { PhotoCamera } from '@mui/icons-material';
import { menuService } from '../../services/menuService';

interface MenuItemDialogProps {
  open: boolean;
  item: MenuItemType | null;
  categories: Category[];
  onClose: () => void;
  onSave: (data: Partial<MenuItemType>) => Promise<void>;
}

export const MenuItemDialog: React.FC<MenuItemDialogProps> = ({
  open,
  item,
  categories,
  onClose,
  onSave
}) => {
  const [formData, setFormData] = useState<Partial<MenuItemType>>({
    name: '',
    description: '',
    price: 0,
    category_id: categories[0]?.id || 0,
    is_vegetarian: false,
    is_vegan: false,
    is_gluten_free: false,
    spice_level: 0,
    preparation_time: 15,
    allergens: [],
    customization_options: {}
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string>('');

  useEffect(() => {
    if (item) {
      setFormData({
        name: item.name,
        description: item.description,
        price: item.price,
        category_id: item.category_id,
        is_vegetarian: item.is_vegetarian,
        is_vegan: item.is_vegan,
        is_gluten_free: item.is_gluten_free,
        spice_level: item.spice_level,
        preparation_time: item.preparation_time,
        allergens: [...item.allergens],
        customization_options: { ...item.customization_options }
      });
      setImagePreview(item.image_url || '');
    } else {
      setFormData({
        name: '',
        description: '',
        price: 0,
        category_id: categories[0]?.id || 0,
        is_vegetarian: false,
        is_vegan: false,
        is_gluten_free: false,
        spice_level: 0,
        preparation_time: 15,
        allergens: [],
        customization_options: {}
      });
      setImagePreview('');
    }
    setImageFile(null);
    setError('');
  }, [item, categories]);

  const handleChange = (field: keyof MenuItemType, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const validateForm = () => {
    if (!formData.name?.trim()) {
      setError('Name is required');
      return false;
    }
    if (!formData.price || formData.price <= 0) {
      setError('Price must be greater than 0');
      return false;
    }
    if (!formData.category_id) {
      setError('Category is required');
      return false;
    }
    return true;
  };

  const handleImageChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      if (!file.type.startsWith('image/')) {
        setError('Please select an image file');
        return;
      }
      setImageFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async () => {
    if (!validateForm()) return;

    try {
      setLoading(true);
      let savedItem;
      
      // First save the menu item
      if (item) {
        savedItem = await menuService.updateMenuItem(item.id, formData as MenuItemUpdate);
      } else {
        savedItem = await menuService.createMenuItem(formData as MenuItemCreate);
      }
      
      // If there's a new image file, upload it
      if (imageFile && savedItem.id) {
        try {
          const updatedItem = await menuService.uploadImage(savedItem.id, imageFile);
          console.log('Image uploaded successfully:', updatedItem); // Debug log
          savedItem = updatedItem;
        } catch (error) {
          console.error('Failed to upload image:', error);
          setError('Failed to upload image. Please try again.');
          return;
        }
      }
      
      await onSave(savedItem);
      onClose();
    } catch (error) {
      setError('Failed to save menu item. Please try again.');
      console.error('Failed to save menu item:', error);
    } finally {
      setLoading(false);
    }
  };

  const commonAllergens = [
    'dairy', 'eggs', 'fish', 'shellfish', 'tree_nuts',
    'peanuts', 'wheat', 'soy', 'sesame'
  ];

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>{item ? 'Edit Menu Item' : 'Add Menu Item'}</DialogTitle>
      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Box sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
          {imagePreview && (
            <Box
              component="img"
              src={imagePreview}
              alt="Menu item preview"
              sx={{
                width: 100,
                height: 100,
                objectFit: 'cover',
                borderRadius: 1
              }}
            />
          )}
          <label htmlFor="icon-button-file">
            <input
              accept="image/*"
              id="icon-button-file"
              type="file"
              style={{ display: 'none' }}
              onChange={handleImageChange}
            />
            <Button
              variant="outlined"
              component="span"
              startIcon={<PhotoCamera />}
            >
              {imagePreview ? 'Change Image' : 'Upload Image'}
            </Button>
          </label>
        </Box>

        <TextField
          autoFocus
          margin="dense"
          label="Name"
          fullWidth
          required
          value={formData.name || ''}
          onChange={(e) => handleChange('name', e.target.value)}
          error={!!error && !formData.name?.trim()}
        />

        <TextField
          margin="dense"
          label="Description"
          fullWidth
          multiline
          rows={3}
          value={formData.description || ''}
          onChange={(e) => handleChange('description', e.target.value)}
        />

        <TextField
          margin="dense"
          label="Price"
          fullWidth
          required
          type="number"
          inputProps={{ step: '0.01', min: '0' }}
          value={formData.price || ''}
          onChange={(e) => handleChange('price', parseFloat(e.target.value))}
          error={!!error && (!formData.price || formData.price <= 0)}
        />

        <FormControl fullWidth margin="dense">
          <InputLabel>Category</InputLabel>
          <Select
            value={formData.category_id || ''}
            label="Category"
            onChange={(e) => handleChange('category_id', e.target.value)}
          >
            {categories.map((category) => (
              <MenuItem key={category.id} value={category.id}>
                {category.name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <Box sx={{ mt: 2 }}>
          <Typography gutterBottom>Spice Level</Typography>
          <Slider
            value={formData.spice_level || 0}
            onChange={(_, value) => handleChange('spice_level', value)}
            step={1}
            marks
            min={0}
            max={5}
            valueLabelDisplay="auto"
          />
        </Box>

        <TextField
          margin="dense"
          label="Preparation Time (minutes)"
          fullWidth
          type="number"
          inputProps={{ min: '1', step: '1' }}
          value={formData.preparation_time || ''}
          onChange={(e) => handleChange('preparation_time', parseInt(e.target.value))}
        />

        <Box sx={{ mt: 2 }}>
          <Typography gutterBottom>Dietary Options</Typography>
          <FormControlLabel
            control={
              <Switch
                checked={formData.is_vegetarian || false}
                onChange={(e) => handleChange('is_vegetarian', e.target.checked)}
              />
            }
            label="Vegetarian"
          />
          <FormControlLabel
            control={
              <Switch
                checked={formData.is_vegan || false}
                onChange={(e) => handleChange('is_vegan', e.target.checked)}
              />
            }
            label="Vegan"
          />
          <FormControlLabel
            control={
              <Switch
                checked={formData.is_gluten_free || false}
                onChange={(e) => handleChange('is_gluten_free', e.target.checked)}
              />
            }
            label="Gluten Free"
          />
        </Box>

        <Box sx={{ mt: 2 }}>
          <Typography gutterBottom>Allergens</Typography>
          <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
            {commonAllergens.map((allergen) => (
              <Chip
                key={allergen}
                label={allergen.replace('_', ' ')}
                onClick={() => {
                  const allergens = formData.allergens || [];
                  const newAllergens = allergens.includes(allergen)
                    ? allergens.filter(a => a !== allergen)
                    : [...allergens, allergen];
                  handleChange('allergens', newAllergens);
                }}
                color={formData.allergens?.includes(allergen) ? 'primary' : 'default'}
                variant={formData.allergens?.includes(allergen) ? 'filled' : 'outlined'}
                sx={{ mb: 1 }}
              />
            ))}
          </Stack>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          color="primary"
          disabled={loading}
        >
          {item ? 'Update' : 'Create'}
        </Button>
      </DialogActions>
    </Dialog>
  );
}; 