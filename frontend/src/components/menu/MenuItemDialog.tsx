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
  Stack,
  OutlinedInput,
  SelectChangeEvent
} from '@mui/material';
import { MenuItem as MenuItemType, Category, MenuItemUpdate, MenuItemCreate, Allergen } from '../../types/menu';
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
    customization_options: {},
    is_active: true
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string>('');
  const [allergens, setAllergens] = useState<Allergen[]>([]);

  useEffect(() => {
    const loadAllergens = async () => {
      try {
        console.log('Loading allergens...');
        const allAllergens = await menuService.getAllergens();
        console.log('Loaded allergens:', allAllergens);
        setAllergens(allAllergens);
      } catch (error) {
        console.error('Failed to load allergens:', error);
        setError('Failed to load allergens. Please try again.');
      }
    };
    loadAllergens();
  }, []);

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
        allergens: Array.isArray(item.allergens) ? [...item.allergens] : [],
        customization_options: { ...item.customization_options },
        is_active: item.is_active
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
        customization_options: {},
        is_active: true
      });
      setImagePreview('');
    }
    setImageFile(null);
    setError('');
  }, [item, categories]);

  const handleChange = (field: keyof MenuItemType, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleAllergenChange = (allergenId: number) => {
    const currentAllergens = formData.allergens || [];
    const allergen = allergens.find(a => a.id === allergenId);
    
    if (!allergen) return;
    
    const newAllergens = currentAllergens.some(a => a.id === allergenId)
      ? currentAllergens.filter(a => a.id !== allergenId)
      : [...currentAllergens, allergen];
    
    console.log('Allergen toggle:', {
      allergenId,
      currentAllergens,
      newAllergens
    });
    
    setFormData(prev => ({
      ...prev,
      allergens: newAllergens
    }));
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
      
      // Log initial form data
      console.log('Form data before submission:', formData);
      console.log('Allergens in form data:', formData.allergens);
      
      const dataToSave: MenuItemCreate = {
        name: formData.name || '',
        description: formData.description || '',
        price: Number(formData.price) || 0,
        category_id: Number(formData.category_id) || 0,
        is_active: Boolean(formData.is_active),
        is_vegetarian: Boolean(formData.is_vegetarian),
        is_vegan: Boolean(formData.is_vegan),
        is_gluten_free: Boolean(formData.is_gluten_free),
        spice_level: Number(formData.spice_level) || 0,
        preparation_time: Number(formData.preparation_time) || 0,
        allergen_ids: formData.allergens?.map(allergen => allergen.id) || [],
        customization_options: formData.customization_options || {},
        average_rating: 0,
        rating_count: 0
      };
      
      // Log the exact data being sent
      console.log('Data being sent to API:', JSON.stringify(dataToSave, null, 2));
      
      let savedItem;
      if (item) {
        console.log('Updating item with ID:', item.id);
        savedItem = await menuService.updateMenuItem(item.id, dataToSave);
      } else {
        console.log('Creating new item');
        savedItem = await menuService.createMenuItem(dataToSave);
      }
      
      // Log the response
      console.log('API Response:', savedItem);
      console.log('Allergens in response:', savedItem?.allergens);
      
      if (imageFile && savedItem?.id) {
        try {
          const updatedItem = await menuService.uploadImage(savedItem.id, imageFile);
          console.log('Image uploaded successfully:', updatedItem);
          savedItem = updatedItem;
        } catch (error) {
          console.error('Failed to upload image:', error);
          setError('Failed to upload image. Please try again.');
          return;
        }
      }
      
      if (savedItem) {
        await onSave(savedItem);
        onClose();
      } else {
        throw new Error('Failed to save menu item: No response from server');
      }
    } catch (error: any) {
      console.error('Failed to save menu item:', error);
      let errorMessage = 'Failed to save menu item. Please try again.';
      if (error.response?.data?.detail) {
        errorMessage = typeof error.response.data.detail === 'string' 
          ? error.response.data.detail 
          : 'Validation error occurred. Please check your input.';
      } else if (error.message) {
        errorMessage = error.message;
      }
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>{item ? 'Edit Menu Item' : 'Add Menu Item'}</DialogTitle>
      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            <Typography>{error}</Typography>
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
            {allergens.map((allergen) => (
              <Chip
                key={allergen.id}
                label={allergen.name}
                onClick={() => handleAllergenChange(allergen.id)}
                color={formData.allergens?.some(a => a.id === allergen.id) ? 'primary' : 'default'}
                variant={formData.allergens?.some(a => a.id === allergen.id) ? 'filled' : 'outlined'}
                sx={{ m: 0.5 }}
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