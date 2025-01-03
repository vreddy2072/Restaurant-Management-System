import React, { useState } from 'react';
import {
  Container,
  Tabs,
  Tab,
  Box,
  Typography,
  Paper
} from '@mui/material';
import { CategoryList } from '../components/menu/CategoryList';
import { MenuItemList } from '../components/menu/MenuItemList';

export const MenuManagement: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Menu Management
        </Typography>
        
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
  );
}; 