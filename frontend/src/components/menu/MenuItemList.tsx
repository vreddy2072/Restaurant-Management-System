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
  Fab
} from '@mui/material';
import {
  Search as SearchIcon,
  FilterList as FilterIcon,
  Clear as ClearIcon,
  ViewModule as GridIcon,
  ViewList as ListIcon,
  Add as AddIcon
} from '@mui/icons-material';
import { MenuItemCard } from './MenuItemCard';
import { MenuItemListView } from './MenuItemListView';
import { menuService } from '../../services/menuService';
import type { MenuItem, Category} from '../../types/menu';
import { MenuItemDialog } from './MenuItemDialog';

export const MenuItemList: React.FC = () => {
  const [items, setItems] = useState<MenuItem[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedItem, setSelectedItem] = useState<MenuItem | null>(null);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [filters, setFilters] = useState({
    search: '',
    category: 'all',
    dietary: [] as string[],
    sort: 'name'
  });

  const loadData = async () => {
    try {
      setLoading(true);
      const [menuItems, categoryList] = await Promise.all([
        menuService.getMenuItems(),
        menuService.getCategories()
      ]);
      setItems(menuItems);
      setCategories(categoryList);
    } catch (error) {
      setError('Failed to load data. Please try again.');
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

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

  const handleFilterChange = (key: string, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value }));
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

  const filterItems = () => {
    const filteredItems = items
      .filter(item => {
        const matchesSearch = item.name.toLowerCase().includes(filters.search.toLowerCase()) ||
          item.description.toLowerCase().includes(filters.search.toLowerCase());
        const matchesCategory = filters.category === 'all' || item.category_id === Number(filters.category);
        const matchesDietary = filters.dietary.length === 0 || filters.dietary.every(pref => {
          switch (pref) {
            case 'vegan': return item.is_vegan;
            case 'vegetarian': return item.is_vegetarian;
            case 'gluten_free': return item.is_gluten_free;
            default: return true;
          }
        });
        return matchesSearch && matchesCategory && matchesDietary;
      })
      .sort((a, b) => {
        switch (filters.sort) {
          case 'name': return a.name.localeCompare(b.name);
          case 'price': return a.price - b.price;
          case 'rating': return b.average_rating - a.average_rating;
          default: return 0;
        }
      });
    return filteredItems;
  };

  const renderFilterBar = () => (
    <Box sx={{ mb: 3, display: 'flex', gap: 2, alignItems: 'center' }}>
      <TextField
        size="small"
        placeholder="Search menu items..."
        value={filters.search}
        onChange={(e) => handleFilterChange('search', e.target.value)}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <SearchIcon />
            </InputAdornment>
          ),
          endAdornment: filters.search && (
            <InputAdornment position="end">
              <IconButton size="small" onClick={() => handleFilterChange('search', '')}>
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
          onChange={(e) => handleFilterChange('category', e.target.value)}
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
      {renderViewToggle()}
    </Box>
  );

  const renderContent = () => {
    if (loading) {
      return <div>Loading...</div>;
    }

    if (error) {
      return <Alert severity="error">{error}</Alert>;
    }

    const filteredItems = filterItems();

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