import React, { useState, useCallback, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Box,
  Button,
  Container,
  FormControl,
  FormLabel,
  TextField,
  Radio,
  RadioGroup,
  FormControlLabel,
  Typography,
  Paper,
  useTheme,
  alpha,
  Fade,
  Grow
} from '@mui/material';
import { RestaurantMenu, Group, Person } from '@mui/icons-material';
import { createOrder } from '../services/orderService';
import { useAuth } from '../contexts/AuthContext';
import { useSnackbar } from '../contexts/SnackbarContext';

const Home: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const { showSnackbar } = useSnackbar();
  const { guestLogin } = useAuth();
  const [orderType, setOrderType] = useState<'individual' | 'group'>('individual');
  const [customerName, setCustomerName] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [tableNo] = useState(() => Math.floor(Math.random() * 10) + 1);

  useEffect(() => {
    // Debug current location
    console.log('Current location:', location);
  }, [location]);

  const handleStartOrder = async () => {
    if (!customerName.trim()) {
      showSnackbar('Please enter customer name', 'error');
      return;
    }

    try {
      setIsLoading(true);
      
      // Step 1: Guest Login
      console.log('Attempting guest login...');
      const guestLoginResult = await guestLogin();
      console.log('Guest login successful:', guestLoginResult);
      
      // Step 2: Create Order
      console.log('Creating order...');
      const order = await createOrder({
        customer_name: customerName,
        is_group_order: orderType === 'group'
      });

      if (!order || !order.order_number) {
        throw new Error('Invalid order response');
      }

      // Step 3: Store Order Info
      console.log('Storing order info...', order);
      localStorage.setItem('orderNumber', order.order_number);
      localStorage.setItem('customerName', customerName);
      localStorage.setItem('tableNo', String(tableNo));
      localStorage.setItem('orderType', orderType);

      // Step 4: Navigate
      console.log('Attempting navigation to menu...');
      try {
        navigate('/menu', { replace: true });
        console.log('Navigation successful');
      } catch (navError) {
        console.error('Navigation failed:', navError);
        // Fallback navigation
        window.location.href = '/menu';
      }
    } catch (error: any) {
      console.error('Error starting order:', {
        error,
        response: error.response,
        data: error.response?.data,
        status: error.response?.status,
        message: error.message
      });
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to start order. Please try again.';
      showSnackbar(errorMessage, 'error');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Box
      sx={{
        height: '75vh',
        overflow: 'hidden',
        display: 'flex',
        alignItems: 'center',
        background: `linear-gradient(45deg, ${alpha(theme.palette.primary.main, 0.05)}, ${alpha(theme.palette.secondary.main, 0.05)})`,
        py: 0,
        px: 2
      }}
    >
      <Container 
        maxWidth="md" 
        sx={{ 
          height: 'auto',
          maxHeight: '100vh'
        }}
      >
        <Box sx={{ 
          display: 'flex', 
          flexDirection: 'column',
          maxHeight: '100vh'
        }}>
          <Fade in timeout={1000}>
            <Box sx={{ textAlign: 'center', mb: 1 }}>
              <RestaurantMenu 
                sx={{ 
                  fontSize: { xs: 28, md: 36 },
                  color: theme.palette.primary.main,
                  mb: 0.5
                }} 
              />
              <Typography 
                variant="h3" 
                component="h1" 
                sx={{
                  fontSize: { xs: '1.25rem', md: '1.75rem' },
                  lineHeight: 1.2,
                  fontWeight: 700,
                  background: `linear-gradient(45deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
                  backgroundClip: 'text',
                  textFillColor: 'transparent',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  mb: 0.5
                }}
              >
                Welcome to Our Restaurant
              </Typography>
              <Typography 
                variant="h5" 
                color="text.secondary"
                sx={{ 
                  fontSize: { xs: '0.875rem', md: '1rem' },
                  fontWeight: 500,
                  lineHeight: 1
                }}
              >
                Table {tableNo}
              </Typography>
            </Box>
          </Fade>

          <Grow in timeout={1500}>
            <Paper 
              elevation={0}
              sx={{ 
                p: { xs: 1.5, md: 2 },
                borderRadius: 4,
                background: alpha('#fff', 0.9),
                backdropFilter: 'blur(10px)',
                border: `1px solid ${alpha(theme.palette.primary.main, 0.1)}`
              }}
            >
              <Box sx={{ 
                display: 'flex', 
                flexDirection: 'column', 
                gap: { xs: 1, md: 1.5 },
                '& > .MuiFormControl-root:last-of-type': {
                  mb: { xs: 1, md: 1.5 }
                }
              }}>
                <FormControl>
                  <FormLabel 
                    sx={{ 
                      mb: 0.5,
                      fontSize: '0.875rem',
                      color: 'text.primary',
                      fontWeight: 500
                    }}
                  >
                    Select Order Type
                  </FormLabel>
                  <RadioGroup
                    row
                    value={orderType}
                    onChange={(e) => setOrderType(e.target.value as 'individual' | 'group')}
                    sx={{
                      gap: 1.5,
                      justifyContent: 'center'
                    }}
                  >
                    <Paper 
                      elevation={orderType === 'individual' ? 2 : 0}
                      sx={{ 
                        borderRadius: 2,
                        overflow: 'hidden',
                        flex: 1,
                        maxWidth: { xs: 150, md: 180 },
                        transition: 'all 0.3s ease',
                        border: `1px solid ${orderType === 'individual' ? theme.palette.primary.main : alpha(theme.palette.divider, 0.1)}`,
                      }}
                    >
                      <FormControlLabel
                        value="individual"
                        control={<Radio sx={{ display: 'none' }} />}
                        label={
                          <Box sx={{ 
                            p: { xs: 1, md: 2 },
                            textAlign: 'center',
                            color: orderType === 'individual' ? 'primary.main' : 'text.secondary'
                          }}>
                            <Person sx={{ fontSize: { xs: 30, md: 36 }, mb: 0.5 }} />
                            <Typography variant="body2" sx={{ fontWeight: 500 }}>
                              Individual Order
                            </Typography>
                          </Box>
                        }
                        sx={{ 
                          m: 0,
                          width: '100%',
                          '& .MuiFormControlLabel-label': { width: '100%' }
                        }}
                      />
                    </Paper>

                    <Paper 
                      elevation={orderType === 'group' ? 2 : 0}
                      sx={{ 
                        borderRadius: 2,
                        overflow: 'hidden',
                        flex: 1,
                        maxWidth: { xs: 150, md: 180 },
                        transition: 'all 0.3s ease',
                        border: `1px solid ${orderType === 'group' ? theme.palette.primary.main : alpha(theme.palette.divider, 0.1)}`,
                      }}
                    >
                      <FormControlLabel
                        value="group"
                        control={<Radio sx={{ display: 'none' }} />}
                        label={
                          <Box sx={{ 
                            p: { xs: 1, md: 2 },
                            textAlign: 'center',
                            color: orderType === 'group' ? 'primary.main' : 'text.secondary'
                          }}>
                            <Group sx={{ fontSize: { xs: 30, md: 36 }, mb: 0.5 }} />
                            <Typography variant="body2" sx={{ fontWeight: 500 }}>
                              Group Order
                            </Typography>
                          </Box>
                        }
                        sx={{ 
                          m: 0,
                          width: '100%',
                          '& .MuiFormControlLabel-label': { width: '100%' }
                        }}
                      />
                    </Paper>
                  </RadioGroup>
                </FormControl>

                <FormControl>
                  <FormLabel 
                    sx={{ 
                      mb: 0.5,
                      fontSize: '0.875rem',
                      color: 'text.primary',
                      fontWeight: 500
                    }}
                  >
                    Enter Your Name
                  </FormLabel>
                  <TextField
                    fullWidth
                    placeholder="Enter your name to start ordering"
                    value={customerName}
                    onChange={(e) => setCustomerName(e.target.value)}
                    variant="outlined"
                    size="small"
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        borderRadius: 2,
                        backgroundColor: alpha(theme.palette.background.paper, 0.5),
                        '&:hover': {
                          backgroundColor: alpha(theme.palette.background.paper, 0.8),
                        },
                        '&.Mui-focused': {
                          backgroundColor: alpha(theme.palette.background.paper, 1),
                        }
                      }
                    }}
                  />
                </FormControl>

                <Button
                  variant="contained"
                  size="medium"
                  onClick={handleStartOrder}
                  disabled={isLoading}
                  sx={{
                    py: { xs: 0.75, md: 1 },
                    px: { xs: 3, md: 4 },
                    borderRadius: 2,
                    fontSize: { xs: '0.875rem', md: '1rem' },
                    fontWeight: 600,
                    textTransform: 'none',
                    boxShadow: theme.shadows[4],
                    background: `linear-gradient(45deg, ${theme.palette.primary.main}, ${theme.palette.primary.dark})`,
                    '&:hover': {
                      background: `linear-gradient(45deg, ${theme.palette.primary.dark}, ${theme.palette.primary.main})`,
                    }
                  }}
                >
                  Start Ordering
                </Button>
              </Box>
            </Paper>
          </Grow>
        </Box>
      </Container>
    </Box>
  );
};

export default Home; 