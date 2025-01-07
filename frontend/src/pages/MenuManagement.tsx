import React, { useState } from 'react';
import {
  Container,
  Tabs,
  Tab,
  Box,
  Typography,
  Paper,
  Alert,
  CircularProgress
} from '@mui/material';
import { CategoryList } from '../components/menu/CategoryList';
import { MenuItemList } from '../components/menu/MenuItemList';

export const MenuManagement: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Container maxWidth="lg">
        <Paper sx={{ p: 3 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            Menu Management
          </Typography>
          
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
            <Tabs value={activeTab} onChange={handleTabChange}>
              <Tab label="Categories" />
              <Tab label="Menu Items" />
            </Tabs>
          </Box>

          {activeTab === 0 && (
            <CategoryList />
          )}

          {activeTab === 1 && (
            <MenuItemList />
          )}
        </Paper>
      </Container>
    </Box>
  );
}; 