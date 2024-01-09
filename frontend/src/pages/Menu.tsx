import React, { useState, useEffect, useCallback } from 'react';
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
  IconButton,
  Drawer,
  Button,
  InputAdornment,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Divider,
  Card,
  CardContent,
  Snackbar,
  Alert,
} from '@mui/material';
import {
  FilterList as FilterIcon,
  Search as SearchIcon,
  TuneOutlined as FilterSettingsIcon,
  Add as AddIcon,
} from '@mui/icons-material';
import MenuItemCard from '../components/menu/MenuItemCard';
import { MenuItem as MenuItemType } from '../types/menu';
import { menuService } from '../services/menuService';
import { MenuFilters, MenuFilterValues } from '../components/menu/MenuFilters';
import { useCart } from '../contexts/CartContext';
import RatingComponent from '../components/menu/RatingComponent';
import { ratingService, RatingAverage } from '../services/ratingService';

const Menu: React.FC = () => {
  const { addToCart, loading: cartLoading } = useCart();
  const [menuItems, setMenuItems] = useState<MenuItemType[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const [filterDrawerOpen, setFilterDrawerOpen] = useState(false);
  const [itemAverageRatings, setItemAverageRatings] = useState<Record<number, number>>({});
  const [activeFilters, setActiveFilters] = useState<MenuFilterValues>({
    is_vegetarian: false,
    is_vegan: false,
    is_gluten_free: false,
    allergen_exclude: []
  });

  const fetchMenuItems = React.useCallback(async () => {
    try {
      const items = await menuService.getMenuItems();
      setMenuItems(items);
      
      // Fetch all average ratings at once
      const ratingsPromises = items.map(item => 
        ratingService.getAverageRating(item.id)
          .then(average => ({ id: item.id, average: average.average }))
      );
      const ratings = await Promise.all(ratingsPromises);
      const ratingsMap = ratings.reduce((acc, { id, average }) => {
        acc[id] = average;
        return acc;
      }, {} as Record<number, number>);
      setItemAverageRatings(ratingsMap);
      
      setError(null);
    } catch (err) {
      console.error('Error fetching menu items:', err);
      setError('Failed to load menu items. Please try again later.');
    } finally {
      setLoading(false);
    }
  }, []); // Empty dependency array since menuService is stable

  useEffect(() => {
    if (loading) {
      fetchMenuItems();
    }
  }, [loading, fetchMenuItems]);

  const getAllergens = () => {
    const allergenSet = new Set<string>();
    menuItems.forEach(item => {
      if (Array.isArray(item.allergens)) {
        item.allergens.forEach(allergen => {
          if (allergen && allergen.name) allergenSet.add(allergen.name);
        });
      }
    });
    return Array.from(allergenSet);
  };

  const handleFilterChange = (newFilters: MenuFilterValues) => {
    setActiveFilters(newFilters);
  };

  const filteredMenuItems = React.useMemo(() => {
    return menuItems.filter(item => {
      // Apply search filter
      const matchesSearch = !searchQuery || 
        item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.description.toLowerCase().includes(searchQuery.toLowerCase());

      // Apply category filter
      const matchesCategory = categoryFilter === 'all' || item.category === categoryFilter;

      // Apply dietary filters
      const matchesDietary = (
        (!activeFilters.is_vegetarian || item.is_vegetarian) &&
        (!activeFilters.is_vegan || item.is_vegan) &&
        (!activeFilters.is_gluten_free || item.is_gluten_free)
      );

      // Apply allergen filters
      const matchesAllergens = !activeFilters.allergen_exclude?.length || 
        !item.allergens?.some(allergen => 
          activeFilters.allergen_exclude.includes(allergen.name)
        );

      // Apply rating filter using the stored average ratings
      const itemAverageRating = itemAverageRatings[item.id] || 0;
      const matchesRating = !activeFilters.min_rating || 
        (itemAverageRating >= activeFilters.min_rating);

      return matchesSearch && matchesCategory && matchesDietary && matchesAllergens && matchesRating;
    });
  }, [menuItems, searchQuery, categoryFilter, activeFilters, itemAverageRatings]);

  const categories = ['all', ...new Set(menuItems
    .filter(item => item.category)
    .map(item => item.category)
  )];

  const capitalizeCategory = (category: string) => {
    if (!category) return '';
    return category.charAt(0).toUpperCase() + category.slice(1);
  };

  const groupedMenuItems = filteredMenuItems.reduce((acc, item) => {
    const category = item.category || 'Uncategorized';
    if (!acc[category]) {
      acc[category] = [];
    }
    acc[category].push(item);
    return acc;
  }, {} as Record<string, MenuItemType[]>);

  const handleAddToCart = async (item: MenuItemType) => {
    try {
      await addToCart({
        menu_item_id: item.id,
        quantity: 1,
      });
    } catch (err) {
      console.error('Failed to add item to cart:', err);
    }
  };

  const handleRatingChange = useCallback(async (itemId: number, newRating: number) => {
    setMenuItems(prevItems => {
      const updatedItems = [...prevItems];
      const itemIndex = updatedItems.findIndex(mi => mi.id === itemId);
      if (itemIndex !== -1) {
        updatedItems[itemIndex] = {
          ...updatedItems[itemIndex],
          average_rating: newRating
        };
      }
      return updatedItems;
    });
  }, []);

  const handleAverageRatingChange = useCallback((itemId: number, average: RatingAverage) => {
    setItemAverageRatings(prev => ({
      ...prev,
      [itemId]: average.average
    }));
  }, []);

  const renderMenuItem = (item: MenuItemType) => (
    <ListItem
      key={item.id}
      sx={{
        borderRadius: 1,
        mb: 1,
        '&:hover': {
          backgroundColor: 'action.hover',
        },
      }}
    >
      <Box sx={{ display: 'flex', width: '100%', alignItems: 'center' }}>
        <Box
          component="img"
          src={item.image_url || '/placeholder-food.jpg'}
          alt={item.name}
          sx={{
            width: 80,
            height: 80,
            borderRadius: 1,
            objectFit: 'cover',
            mr: 2,
          }}
        />
        <Box sx={{ flex: 1 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <Box>
              <Typography variant="subtitle1" component="div" sx={{ fontWeight: 'bold' }}>
                {item.name}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                {item.description}
              </Typography>
              <Box sx={{ mt: 1 }}>
                <RatingComponent
                  menuItemId={item.id}
                  initialRating={item.average_rating}
                  initialRatingCount={item.rating_count || 0}
                  onRatingChange={(newRating) => handleRatingChange(item.id, newRating)}
                  onAverageRatingChange={(average) => handleAverageRatingChange(item.id, average)}
                />
              </Box>
              <Box sx={{ mt: 1, display: 'flex', gap: 1 }}>
                {item.is_vegetarian && (
                  <Typography variant="caption" sx={{ color: 'success.main' }}>
                    Vegetarian
                  </Typography>
                )}
                {item.is_vegan && (
                  <Typography variant="caption" sx={{ color: 'success.main' }}>
                    Vegan
                  </Typography>
                )}
                {item.is_gluten_free && (
                  <Typography variant="caption" sx={{ color: 'success.main' }}>
                    Gluten Free
                  </Typography>
                )}
                {item.spice_level > 0 && (
                  <Typography variant="caption" sx={{ color: 'error.main' }}>
                    Spice Level: {item.spice_level}
                  </Typography>
                )}
              </Box>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Typography variant="h6" component="div" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                ${item.price.toFixed(2)}
              </Typography>
              <Button
                variant="contained"
                size="small"
                startIcon={<AddIcon />}
                onClick={() => handleAddToCart(item)}
                disabled={cartLoading}
                sx={{ minWidth: 100 }}
              >
                Add
              </Button>
            </Box>
          </Box>
        </Box>
      </Box>
    </ListItem>
  );

  const renderCategorySection = (category: string, items: MenuItemType[]) => (
    <Box key={category} sx={{ mb: 4 }}>
      <Typography
        variant="h5"
        component="h2"
        sx={{
          mb: 2,
          pb: 1,
          borderBottom: '2px solid',
          borderColor: 'primary.main',
          fontWeight: 'bold',
        }}
      >
        {capitalizeCategory(category)}
      </Typography>
      <Paper elevation={0} sx={{ bgcolor: 'background.default' }}>
        <List disablePadding>
          {items.map((item) => renderMenuItem(item))}
        </List>
      </Paper>
    </Box>
  );

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
    <Box>
      <Container maxWidth="lg">
        <Box sx={{ mb: 2 }}>
          <Typography variant="h4" component="h1">
            Our Menu
          </Typography>
        </Box>

        <Paper sx={{ p: 2, mb: 2 }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs>
              <TextField
                fullWidth
                size="small"
                placeholder="Search menu items..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon />
                    </InputAdornment>
                  ),
                }}
              />
            </Grid>
            <Grid item xs={3}>
              <FormControl fullWidth size="small">
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
            <Grid item>
              <Button
                variant="outlined"
                startIcon={<FilterSettingsIcon />}
                onClick={() => setFilterDrawerOpen(true)}
                size="medium"
              >
                Filters
              </Button>
            </Grid>
          </Grid>
        </Paper>

        {Object.keys(groupedMenuItems).length === 0 ? (
          <Typography variant="h6" align="center" color="text.secondary">
            No menu items found
          </Typography>
        ) : (
          Object.entries(groupedMenuItems).map(([category, items]) =>
            renderCategorySection(category, items)
          )
        )}
      </Container>

      <Drawer
        anchor="right"
        open={filterDrawerOpen}
        onClose={() => setFilterDrawerOpen(false)}
      >
        <Box sx={{ width: 300, p: 3 }}>
          <MenuFilters
            onFilterChange={handleFilterChange}
            availableAllergens={getAllergens()}
          />
          <Box sx={{ mt: 3 }}>
            <Button
              fullWidth
              variant="contained"
              onClick={() => setFilterDrawerOpen(false)}
            >
              Apply Filters
            </Button>
          </Box>
        </Box>
      </Drawer>
    </Box>
  );
};

export default Menu;