import React, { useState, useEffect } from 'react';
import {
  Grid,
  Box,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem as MuiMenuItem,
  IconButton,
  Tooltip,
  Alert,
  Paper,
  InputAdornment,
  Chip,
  Stack,
  ToggleButtonGroup,
  ToggleButton,
  List,
  Drawer,
  Button,
  Fab
} from '@mui/material';
import {
  Search as SearchIcon,
  FilterList as FilterIcon,
  Clear as ClearIcon,
  ViewModule as GridIcon,
  ViewList as ListIcon,
  TuneOutlined as FilterSettingsIcon,
  Add as AddIcon
} from '@mui/icons-material';
import MenuItemCard from './MenuItemCard';
import { MenuItemListView } from './MenuItemListView';
import { menuService } from '../../services/menuService';
import type { MenuItem, Category } from '../../types/menu';
import { MenuItemDialog } from './MenuItemDialog';
import { MenuFilters } from './MenuFilters';

export const MenuItemList: React.FC = () => {
  const [items, setItems] = useState<MenuItem[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedItem, setSelectedItem] = useState<MenuItem | null>(null);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [filterDrawerOpen, setFilterDrawerOpen] = useState(false);
  const [activeFilters, setActiveFilters] = useState<{
    dietary: string[];
    allergens: string[];
    priceRange: [number, number];
    rating: number;
  }>({
    dietary: [],
    allergens: [],
    priceRange: [0, 100],
    rating: 0
  });
  const [filters, setFilters] = useState({
    search: '',
    category: 'all',
    dietary: [] as string[],
    sort: 'name'
  });

  const handleFilterChange = (newFilters: any) => {
    setActiveFilters(prev => ({
      ...prev,
      dietary: [
        ...(newFilters.is_vegetarian ? ['vegetarian'] : []),
        ...(newFilters.is_vegan ? ['vegan'] : []),
        ...(newFilters.is_gluten_free ? ['gluten_free'] : [])
      ],
      allergens: newFilters.allergen_exclude || [],
      priceRange: [newFilters.min_price || 0, newFilters.max_price || 100],
      rating: newFilters.min_rating || 0
    }));
  };

  const getAllergens = () => {
    const allergenSet = new Set<string>();
    items.forEach(item => {
      console.log('Processing item:', item.name, 'allergens:', item.allergens); // Debug log
      if (Array.isArray(item.allergens)) {
        item.allergens.forEach(allergen => {
          if (allergen && allergen.name) allergenSet.add(allergen.name);
        });
      }
    });
    const allergens = Array.from(allergenSet);
    console.log('Final allergens list:', allergens); // Debug log
    return allergens;
  };

  const filterItems = () => {
    console.log('Filtering items with:', {
      searchTerm: filters.search,
      category: filters.category,
      dietary: activeFilters.dietary,
      allergens: activeFilters.allergens,
      priceRange: activeFilters.priceRange,
      rating: activeFilters.rating
    });

    return items.filter(item => {
      // Search filter
      const matchesSearch = item.name.toLowerCase().includes(filters.search.toLowerCase()) ||
        (item.description?.toLowerCase() || '').includes(filters.search.toLowerCase());

      // Category filter
      const matchesCategory = filters.category === 'all' || item.category_id === Number(filters.category);

      // Dietary preferences
      const matchesDietary = activeFilters.dietary.length === 0 || activeFilters.dietary.every(pref => {
        switch (pref) {
          case 'vegetarian': return item.is_vegetarian;
          case 'vegan': return item.is_vegan;
          case 'gluten_free': return item.is_gluten_free;
          default: return true;
        }
      });

      // Allergens
      const matchesAllergens = activeFilters.allergens.length === 0 ||
        !activeFilters.allergens.some(allergen => 
          item.allergens?.some(itemAllergen => itemAllergen.name === allergen)
        );

      // Price range
      const matchesPrice = item.price >= activeFilters.priceRange[0] &&
        item.price <= activeFilters.priceRange[1];

      // Rating
      const matchesRating = item.average_rating >= activeFilters.rating;

      const matches = {
        search: matchesSearch,
        category: matchesCategory,
        dietary: matchesDietary,
        allergens: matchesAllergens,
        price: matchesPrice,
        rating: matchesRating
      };

      console.log(`Filtering item "${item.name}":`, matches);

      return matchesSearch && matchesCategory && matchesDietary && 
        matchesAllergens && matchesPrice && matchesRating;
    });
  };

  const handleEdit = (item: MenuItem) => {
    setSelectedItem(item);
    setDialogOpen(true);
  };

  const handleDelete = async (item: MenuItem) => {
    if (window.confirm('Are you sure you want to delete this item?')) {
      try {
        await menuService.deleteMenuItem(item.id);
        setItems(items.filter(i => i.id !== item.id));
      } catch (error) {
        setError('Failed to delete item. Please try again.');
        console.error('Failed to delete item:', error);
      }
    }
  };

  const handleToggleActive = async (item: MenuItem) => {
    try {
      const { id, ...itemWithoutId } = item;
      const updatedItem = await menuService.updateMenuItem(id, {
        ...itemWithoutId,
        is_active: !item.is_active
      });
      setItems(items.map(i => i.id === item.id ? updatedItem : i));
    } catch (error) {
      setError('Failed to update item status. Please try again.');
      console.error('Failed to update item status:', error);
    }
  };

  const handleAddItem = () => {
    setSelectedItem(null);
    setDialogOpen(true);
  };

  const handleDialogClose = () => {
    setDialogOpen(false);
    setSelectedItem(null);
  };

  const handleDialogSave = async (itemData: Partial<MenuItem>) => {
    try {
      if (selectedItem) {
        setItems(items.map(item => 
          item.id === selectedItem.id ? itemData as MenuItem : item
        ));
      } else {
        setItems([...items, itemData as MenuItem]);
      }
      handleDialogClose();
      await loadData();
    } catch (error) {
      setError('Failed to save item. Please try again.');
      console.error('Failed to save item:', error);
    }
  };

  const handleViewModeChange = (
    event: React.MouseEvent<HTMLElement>,
    newMode: 'grid' | 'list' | null
  ) => {
    if (newMode !== null) {
      setViewMode(newMode);
    }
  };

  const renderViewToggle = () => (
    <ToggleButtonGroup
      value={viewMode}
      exclusive
      onChange={handleViewModeChange}
      size="small"
      aria-label="view mode"
    >
      <ToggleButton value="grid" aria-label="grid view">
        <Tooltip title="Grid View">
          <GridIcon />
        </Tooltip>
      </ToggleButton>
      <ToggleButton value="list" aria-label="list view">
        <Tooltip title="List View">
          <ListIcon />
        </Tooltip>
      </ToggleButton>
    </ToggleButtonGroup>
  );

  const renderFilterBar = () => (
    <Box sx={{ mb: 3 }}>
      <Paper sx={{ p: 2 }}>
        <Stack spacing={2}>
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
            <TextField
              size="small"
              placeholder="Search menu items..."
              value={filters.search}
              onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
                endAdornment: filters.search && (
                  <InputAdornment position="end">
                    <IconButton size="small" onClick={() => setFilters(prev => ({ ...prev, search: '' }))}>
                      <ClearIcon />
                    </IconButton>
                  </InputAdornment>
                )
              }}
              sx={{ flexGrow: 1 }}
            />
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>Category</InputLabel>
              <Select
                value={filters.category}
                onChange={(e) => setFilters(prev => ({ ...prev, category: e.target.value }))}
                label="Category"
              >
                <MuiMenuItem value="all">All Categories</MuiMenuItem>
                {categories.map((category) => (
                  <MuiMenuItem key={category.id} value={category.id}>
                    {category.name}
                  </MuiMenuItem>
                ))}
              </Select>
            </FormControl>
            <Button
              variant="outlined"
              startIcon={<FilterSettingsIcon />}
              onClick={() => setFilterDrawerOpen(true)}
            >
              Filters
            </Button>
            {renderViewToggle()}
          </Box>
          {(activeFilters.dietary.length > 0 || activeFilters.allergens.length > 0) && (
            <Stack direction="row" spacing={1} flexWrap="wrap">
              {activeFilters.dietary.map((filter) => (
                <Chip
                  key={filter}
                  label={filter.replace('_', ' ')}
                  onDelete={() => {
                    setActiveFilters(prev => ({
                      ...prev,
                      dietary: prev.dietary.filter(f => f !== filter)
                    }));
                  }}
                />
              ))}
              {activeFilters.allergens.map((allergen) => (
                <Chip
                  key={allergen}
                  label={`No ${allergen}`}
                  onDelete={() => {
                    setActiveFilters(prev => ({
                      ...prev,
                      allergens: prev.allergens.filter(a => a !== allergen)
                    }));
                  }}
                />
              ))}
            </Stack>
          )}
        </Stack>
      </Paper>
    </Box>
  );

  const renderContent = () => {
    console.log('Rendering content with state:', {
      loading,
      error,
      itemsCount: items.length,
      categoriesCount: categories.length,
      filters,
      activeFilters
    });

    if (loading) {
      return <div>Loading...</div>;
    }

    if (error) {
      return <Alert severity="error">{error}</Alert>;
    }

    const filteredItems = filterItems();
    console.log('Filtered items:', filteredItems);

    if (filteredItems.length === 0) {
      return <Alert severity="info">No menu items found</Alert>;
    }

    if (viewMode === 'grid') {
      return (
        <Grid container spacing={3}>
          {filteredItems.map((item) => (
            <Grid item xs={12} sm={6} md={4} lg={3} key={item.id}>
              <MenuItemCard
                item={item}
                onEdit={handleEdit}
                onDelete={handleDelete}
                onToggleActive={handleToggleActive}
              />
            </Grid>
          ))}
        </Grid>
      );
    }

    return (
      <List>
        {filteredItems.map((item) => (
          <MenuItemListView
            key={item.id}
            item={item}
            onEdit={handleEdit}
            onDelete={handleDelete}
            onToggleActive={handleToggleActive}
          />
        ))}
      </List>
    );
  };

  const loadData = async () => {
    try {
      setLoading(true);
      console.log('Loading menu data...');
      const [menuItems, categoryList] = await Promise.all([
        menuService.getMenuItems(),
        menuService.getCategories()
      ]);
      console.log('Loaded menu items:', menuItems);
      console.log('Loaded categories:', categoryList);
      setItems(menuItems);
      setCategories(categoryList);
    } catch (error) {
      console.error('Failed to load data:', error);
      setError('Failed to load data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  return (
    <Box sx={{ p: 3 }}>
      {renderFilterBar()}
      {renderContent()}
      <MenuItemDialog
        open={dialogOpen}
        item={selectedItem}
        categories={categories}
        onClose={handleDialogClose}
        onSave={handleDialogSave}
      />
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
        </Box>
      </Drawer>
      <Fab 
        color="primary" 
        sx={{ position: 'fixed', bottom: 16, right: 16 }}
        onClick={handleAddItem}
        aria-label="add menu item"
      >
        <AddIcon />
      </Fab>
    </Box>
  );
};