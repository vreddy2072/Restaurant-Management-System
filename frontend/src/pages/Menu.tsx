import React, { useState, useEffect } from 'react';
import {
  Container,
  Grid,
  Typography,
  TextField,
  Box,
  CircularProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Stack,
} from '@mui/material';
import MenuItemCard from '../components/menu/MenuItemCard';
import { MenuItem as MenuItemType } from '../types/menu';
import { menuService } from '../services/menuService';

const Menu: React.FC = () => {
  const [menuItems, setMenuItems] = useState<MenuItemType[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const [dietaryFilters, setDietaryFilters] = useState<{
    vegetarian: boolean;
    vegan: boolean;
    glutenFree: boolean;
  }>({
    vegetarian: false,
    vegan: false,
    glutenFree: false,
  });

  useEffect(() => {
    fetchMenuItems();
  }, []);

  const fetchMenuItems = async () => {
    try {
      setLoading(true);
      console.log('Fetching menu items...');
      const items = await menuService.getMenuItems();
      console.log('Received menu items:', items);
      setMenuItems(items);
      setError(null);
    } catch (err) {
      console.error('Error fetching menu items:', err);
      setError('Failed to load menu items');
    } finally {
      setLoading(false);
    }
  };

  const filteredMenuItems = menuItems
    .filter(item => {
      // Search filter
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        return (
          item.name.toLowerCase().includes(query) ||
          item.description.toLowerCase().includes(query)
        );
      }
      return true;
    })
    .filter(item => {
      // Category filter
      if (categoryFilter === 'all') return true;
      return item.category === categoryFilter;
    })
    .filter(item => {
      // Dietary filters
      if (dietaryFilters.vegetarian && !item.is_vegetarian) return false;
      if (dietaryFilters.vegan && !item.is_vegan) return false;
      if (dietaryFilters.glutenFree && !item.is_gluten_free) return false;
      return true;
    });

  console.log('Menu items before filtering:', menuItems);
  console.log('Filtered menu items:', filteredMenuItems);

  const categories = ['all', ...new Set(menuItems
    .filter(item => item.category) // Filter out items with undefined category
    .map(item => item.category)
  )];

  const capitalizeCategory = (category: string) => {
    if (!category) return '';
    return category.charAt(0).toUpperCase() + category.slice(1);
  };

  const toggleDietaryFilter = (filter: keyof typeof dietaryFilters) => {
    setDietaryFilters(prev => ({
      ...prev,
      [filter]: !prev[filter],
    }));
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box display="flex" justifyContent="center" p={4}>
        <Typography color="error">{error}</Typography>
      </Box>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Our Menu
      </Typography>

      <Box sx={{ mb: 4 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="Search Menu"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <InputLabel>Category</InputLabel>
              <Select
                value={categoryFilter}
                label="Category"
                onChange={(e) => setCategoryFilter(e.target.value)}
              >
                {categories.map((category) => (
                  <MenuItem key={category} value={category}>
                    {capitalizeCategory(category)}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={4}>
            <Stack direction="row" spacing={1}>
              <Chip
                label="Vegetarian"
                onClick={() => toggleDietaryFilter('vegetarian')}
                color={dietaryFilters.vegetarian ? 'primary' : 'default'}
                variant={dietaryFilters.vegetarian ? 'filled' : 'outlined'}
              />
              <Chip
                label="Vegan"
                onClick={() => toggleDietaryFilter('vegan')}
                color={dietaryFilters.vegan ? 'primary' : 'default'}
                variant={dietaryFilters.vegan ? 'filled' : 'outlined'}
              />
              <Chip
                label="Gluten Free"
                onClick={() => toggleDietaryFilter('glutenFree')}
                color={dietaryFilters.glutenFree ? 'primary' : 'default'}
                variant={dietaryFilters.glutenFree ? 'filled' : 'outlined'}
              />
            </Stack>
          </Grid>
        </Grid>
      </Box>

      {filteredMenuItems.length === 0 ? (
        <Typography variant="h6" align="center" color="text.secondary">
          No menu items found
        </Typography>
      ) : (
        <Grid container spacing={3}>
          {filteredMenuItems.map((item) => (
            <Grid item xs={12} sm={6} md={4} key={item.id}>
              <MenuItemCard
                item={item}
                showAdminControls={false}
                isLoading={loading}
                error={error || undefined}
              />
            </Grid>
          ))}
        </Grid>
      )}
    </Container>
  );
};

export default Menu;
