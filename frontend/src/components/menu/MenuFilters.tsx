import React, { useState } from 'react';
import {
  Box,
  FormGroup,
  FormControlLabel,
  Checkbox,
  Slider,
  Typography,
  Rating,
  Stack
} from '@mui/material';
import { Star as StarIcon } from '@mui/icons-material';

interface MenuFiltersProps {
  onFilterChange: (filters: MenuFilterValues) => void;
  availableAllergens?: string[];
}

export interface MenuFilterValues {
  is_vegetarian: boolean;
  is_vegan: boolean;
  is_gluten_free: boolean;
  min_price?: number;
  max_price?: number;
  min_rating?: number;
  allergen_exclude: string[];
}

export const MenuFilters: React.FC<MenuFiltersProps> = ({
  onFilterChange,
  availableAllergens = []
}) => {
  const [filters, setFilters] = useState<MenuFilterValues>({
    is_vegetarian: false,
    is_vegan: false,
    is_gluten_free: false,
    allergen_exclude: []
  });

  const handleChange = (field: keyof MenuFilterValues, value: any) => {
    const newFilters = { ...filters, [field]: value };
    setFilters(newFilters);
    onFilterChange(newFilters);
  };

  const handleAllergenChange = (allergen: string, checked: boolean) => {
    const newAllergens = checked
      ? [...filters.allergen_exclude, allergen]
      : filters.allergen_exclude.filter(a => a !== allergen);
    handleChange('allergen_exclude', newAllergens);
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>Filters</Typography>
      
      <Box sx={{ mb: 3 }}>
        <Typography gutterBottom>Dietary Preferences</Typography>
        <FormGroup>
          <FormControlLabel
            control={
              <Checkbox
                checked={filters.is_vegetarian}
                onChange={(e) => handleChange('is_vegetarian', e.target.checked)}
              />
            }
            label="Vegetarian"
          />
          <FormControlLabel
            control={
              <Checkbox
                checked={filters.is_vegan}
                onChange={(e) => handleChange('is_vegan', e.target.checked)}
              />
            }
            label="Vegan"
          />
          <FormControlLabel
            control={
              <Checkbox
                checked={filters.is_gluten_free}
                onChange={(e) => handleChange('is_gluten_free', e.target.checked)}
              />
            }
            label="Gluten Free"
          />
        </FormGroup>
      </Box>

      <Box sx={{ mb: 3 }}>
        <Typography gutterBottom>Price Range</Typography>
        <Box sx={{ px: 2 }}>
          <Slider
            value={[filters.min_price || 0, filters.max_price || 100]}
            onChange={(_, value) => {
              const [min, max] = value as number[];
              handleChange('min_price', min);
              handleChange('max_price', max);
            }}
            valueLabelDisplay="auto"
            valueLabelFormat={(value) => `$${value}`}
            min={0}
            max={100}
            step={5}
          />
        </Box>
      </Box>

      <Box sx={{ mb: 3 }}>
        <Typography gutterBottom>Minimum Rating</Typography>
        <Stack spacing={1} alignItems="center">
          <Rating
            value={filters.min_rating || 0}
            onChange={(_, value) => handleChange('min_rating', value)}
            precision={0.5}
            emptyIcon={<StarIcon style={{ opacity: 0.55 }} fontSize="inherit" />}
          />
          <Typography variant="body2" color="text.secondary">
            {filters.min_rating ? `${filters.min_rating} stars and up` : 'No minimum rating'}
          </Typography>
        </Stack>
      </Box>

      <Box sx={{ mb: 3 }}>
        <Typography gutterBottom>Exclude Allergens</Typography>
        <FormGroup>
          {(availableAllergens || []).length > 0 ? (
            availableAllergens.map((allergen) => (
              <FormControlLabel
                key={allergen}
                control={
                  <Checkbox
                    checked={filters.allergen_exclude.includes(allergen)}
                    onChange={(e) => handleAllergenChange(allergen, e.target.checked)}
                  />
                }
                label={allergen.split('_').join(' ')}
              />
            ))
          ) : (
            <Typography variant="body2" color="text.secondary">
              No allergens defined in menu items
            </Typography>
          )}
        </FormGroup>
      </Box>
    </Box>
  );
};