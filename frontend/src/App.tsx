import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { AppBar, Toolbar, Typography, Container, Box, Button } from '@mui/material';
import { MenuManagement } from './pages/MenuManagement';

function App() {
  return (
    <Router>
      <Box sx={{ flexGrow: 1 }}>
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              Restaurant Management
            </Typography>
            <Button color="inherit" component={Link} to="/menu">
              Menu Management
            </Button>
          </Toolbar>
        </AppBar>

        <Container>
          <Routes>
            <Route path="/menu" element={<MenuManagement />} />
            <Route path="/" element={
              <Box sx={{ mt: 4, textAlign: 'center' }}>
                <Typography variant="h4" component="h1" gutterBottom>
                  Welcome to Restaurant Management System
                </Typography>
                <Typography variant="body1" gutterBottom>
                  Use the navigation menu above to manage your restaurant.
                </Typography>
              </Box>
            } />
          </Routes>
        </Container>
      </Box>
    </Router>
  );
}

export default App;
