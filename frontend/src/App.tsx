import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from 'react-router-dom';
import { AppBar, Toolbar, Typography, Container, Box, Button } from '@mui/material';
import { MenuManagement } from './pages/MenuManagement';
import RegisterForm from './components/auth/RegisterForm';
import LoginForm from './components/auth/LoginForm';
import ProtectedRoute from './components/auth/ProtectedRoute';
import { useAuth } from './contexts/AuthContext';

function NavBar() {
  const navigate = useNavigate();
  const { isAuthenticated, logout } = useAuth();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <AppBar position="static" sx={{ minHeight: 56 }}>
      <Toolbar variant="dense" sx={{ minHeight: 56 }}>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Restaurant Management
        </Typography>
        {isAuthenticated ? (
          <>
            <Button color="inherit" component={Link} to="/menu" size="small">
              Menu Management
            </Button>
            <Button color="inherit" onClick={handleLogout} size="small" sx={{ ml: 1 }}>
              Logout
            </Button>
          </>
        ) : (
          <>
            <Button color="inherit" component={Link} to="/login" size="small">
              Login
            </Button>
            <Button color="inherit" component={Link} to="/register" size="small" sx={{ ml: 1 }}>
              Register
            </Button>
          </>
        )}
      </Toolbar>
    </AppBar>
  );
}

function App() {
  return (
    <Router>
      <Box sx={{ 
        display: 'flex', 
        flexDirection: 'column', 
        height: '100%',
        bgcolor: 'background.default'
      }}>
        <NavBar />
        <Box sx={{ flex: 1, position: 'relative' }}>
          <Routes>
            <Route path="/register" element={<RegisterForm />} />
            <Route path="/login" element={<LoginForm />} />
            <Route path="/menu" element={
              <ProtectedRoute>
                <MenuManagement />
              </ProtectedRoute>
            } />
            <Route path="/" element={
              <Box sx={{ 
                height: '100%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                textAlign: 'center',
                p: 3
              }}>
                <Typography variant="h4" component="h1" gutterBottom>
                  Welcome to Restaurant Management System
                </Typography>
              </Box>
            } />
          </Routes>
        </Box>
      </Box>
    </Router>
  );
}

export default App;
