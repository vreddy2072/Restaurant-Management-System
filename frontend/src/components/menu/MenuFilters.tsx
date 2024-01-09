import React, { useState } from 'react';
import {
  Box,
  FormGroup,
  FormControlLabel,
  Checkbox,
  Slider,
  Typography,
} from '@mui/material';

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

      <Box sx={{ mt: 2 }}>
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
            min={0}
            max={100}
            step={5}
          />
        </Box>
      </Box>

      <Box sx={{ mt: 2 }}>
        <Typography gutterBottom>Minimum Rating</Typography>
        <Box sx={{ px: 2 }}>
          <Slider
            value={filters.min_rating || 0}
            onChange={(_, value) => handleChange('min_rating', value)}
            valueLabelDisplay="auto"
            min={0}
            max={5}
            step={0.5}
          />
        </Box>
      </Box>

      <Box sx={{ mt: 2 }}>
        <Typography gutterBottom>Exclude Allergens</Typography>
        <FormGroup>
          {availableAllergens.map((allergen) => (
            <FormControlLabel
              key={allergen}
              control={
                <Checkbox
                  checked={filters.allergen_exclude.includes(allergen)}
                  onChange={(e) => handleAllergenChange(allergen, e.target.checked)}
                />
              }
              label={allergen.replace('_', ' ')}
            />
          ))}
        </FormGroup>
      </Box>
    </Box>
  );
}; 