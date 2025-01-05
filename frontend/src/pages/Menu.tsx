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

const Menu: React.FC = () => {
  const [menuItems, setMenuItems] = useState<MenuItemType[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const [filterDrawerOpen, setFilterDrawerOpen] = useState(false);
  const [activeFilters, setActiveFilters] = useState<MenuFilterValues>({
    is_vegetarian: false,
    is_vegan: false,
    is_gluten_free: false,
    allergen_exclude: []
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
      if (activeFilters.is_vegetarian && !item.is_vegetarian) return false;
      if (activeFilters.is_vegan && !item.is_vegan) return false;
      if (activeFilters.is_gluten_free && !item.is_gluten_free) return false;

      // Price range
      if (activeFilters.min_price !== undefined && item.price < activeFilters.min_price) return false;
      if (activeFilters.max_price !== undefined && item.price > activeFilters.max_price) return false;

      // Rating
      if (activeFilters.min_rating !== undefined && item.average_rating < activeFilters.min_rating) return false;

      // Allergens
      if (activeFilters.allergen_exclude.length > 0) {
        const itemAllergens = item.allergens?.map(a => a.name) || [];
        if (activeFilters.allergen_exclude.some(allergen => itemAllergens.includes(allergen))) {
          return false;
        }
      }

      return true;
    });

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
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4" component="h1">
          Our Menu
        </Typography>
      </Box>

      <Box sx={{ mb: 4 }}>
        <Paper sx={{ p: 2 }}>
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
      </Box>

      {Object.keys(groupedMenuItems).length === 0 ? (
        <Typography variant="h6" align="center" color="text.secondary">
          No menu items found
        </Typography>
      ) : (
        Object.entries(groupedMenuItems).map(([category, items]) =>
          renderCategorySection(category, items)
        )
      )}

      <Drawer
        anchor="right"
        open={filterDrawerOpen}
        onClose={() => setFilterDrawerOpen(false)}
      >
        <Box sx={{ width: 300, p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Filters
          </Typography>
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
    </Container>
  );
};

export default Menu;
