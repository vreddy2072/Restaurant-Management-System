import React, { useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Rating,
  Select,
  MenuItem as MuiMenuItem,
  FormControl,
  InputLabel,
  Alert,
  Box,
  Tooltip,
  IconButton,
  Grid
} from '@mui/material';
import { 
  LocalDining as VegetarianIcon,
  Grass as VeganIcon,
  DoNotTouch as GlutenFreeIcon,
  Whatshot as SpicyIcon
} from '@mui/icons-material';
import { MenuItem } from '../../types/menu';

interface MenuItemDetailProps {
  menuItem: MenuItem;
  onCustomizationChange?: (options: Record<string, string>) => void;
}

export const MenuItemDetail: React.FC<MenuItemDetailProps> = ({ 
  menuItem,
  onCustomizationChange
}) => {
  const [customizations, setCustomizations] = useState<Record<string, string>>({});

  const handleCustomizationChange = (option: string, value: string) => {
    const newCustomizations = {
      ...customizations,
      [option]: value
    };
    setCustomizations(newCustomizations);
    onCustomizationChange?.(newCustomizations);
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h5" component="h2">
          {menuItem.name}
        </Typography>
        
        <Typography variant="body2" color="textSecondary">
          {menuItem.description}
        </Typography>

        <Typography variant="h6" color="primary">
          ${menuItem.price.toFixed(2)}
        </Typography>

        <Typography variant="body2">
          {menuItem.preparation_time} mins preparation time
        </Typography>

        <Box sx={{ my: 2 }}>
          {menuItem.is_vegetarian && (
            <Tooltip title="Suitable for vegetarians">
              <IconButton data-testid="vegetarian-icon">
                <VegetarianIcon />
              </IconButton>
            </Tooltip>
          )}
          {menuItem.is_vegan && (
            <Tooltip title="Suitable for vegans">
              <IconButton data-testid="vegan-icon">
                <VeganIcon />
              </IconButton>
            </Tooltip>
          )}
          {menuItem.is_gluten_free && (
            <Tooltip title="Gluten-free">
              <IconButton data-testid="gluten-free-icon">
                <GlutenFreeIcon />
              </IconButton>
            </Tooltip>
          )}
          <Tooltip title={`Spice Level: ${menuItem.spice_level}`}>
            <IconButton data-testid={`spice-level-${menuItem.spice_level}`}>
              <SpicyIcon />
            </IconButton>
          </Tooltip>
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Rating 
            value={menuItem.average_rating} 
            precision={0.5} 
            readOnly
            aria-label={`${menuItem.average_rating} Stars`}
          />
          <Typography variant="body2" sx={{ ml: 1 }}>
            ({menuItem.rating_count} reviews)
          </Typography>
        </Box>

        {menuItem.allergens && menuItem.allergens.length > 0 && (
          <Alert 
            severity="warning" 
            data-testid="allergen-warnings"
            sx={{ mb: 2 }}
          >
            Contains: {menuItem.allergens.join(', ')}
          </Alert>
        )}

        {menuItem.customization_options && (
          <Box>
            <Typography variant="h6" gutterBottom>
              Customization Options
            </Typography>
            <Grid container spacing={2}>
              {Object.entries(menuItem.customization_options).map(([option, values]) => (
                <Grid item xs={12} sm={6} key={option}>
                  <FormControl fullWidth>
                    <InputLabel id={`${option}-label`}>{option}</InputLabel>
                    <Select
                      labelId={`${option}-label`}
                      value={customizations[option] || ''}
                      label={option}
                      onChange={(e) => handleCustomizationChange(option, e.target.value)}
                    >
                      {values.map((value) => (
                        <MuiMenuItem key={value} value={value}>
                          {value}
                        </MuiMenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
              ))}
            </Grid>
          </Box>
        )}
      </CardContent>
    </Card>
  );
}; 