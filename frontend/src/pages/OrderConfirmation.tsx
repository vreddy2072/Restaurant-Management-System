import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Paper,
  Typography,
  Box,
  Divider,
  List,
  ListItem,
  ListItemText,
  Button,
  CircularProgress,
  Alert
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';

interface OrderItem {
  id: number;
  name: string;
  quantity: number;
  price: number;
  subtotal: number;
}

interface Order {
  order_number: string;
  items: OrderItem[];
  total: number;
  tax: number;
  status: string;
  created_at: string;
}

const OrderConfirmation: React.FC = () => {
  const { orderNumber } = useParams<{ orderNumber: string }>();
  const [order, setOrder] = useState<Order | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  useEffect(() => {
    const fetchOrderDetails = async () => {
      try {
        if (!orderNumber) {
          throw new Error('Order number is required');
        }

        const response = await axios.get(`/api/orders/get_order_by_number/${orderNumber}`);
        setOrder(response.data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch order details');
        console.error('Error fetching order:', err);
      } finally {
        setLoading(false);
      }
    };

    if (isAuthenticated && orderNumber) {
      fetchOrderDetails();
    }
  }, [orderNumber, isAuthenticated]);

  if (!isAuthenticated) {
    return (
      <Container maxWidth="md" sx={{ mt: 4 }}>
        <Alert severity="error">
          Please log in to view order details
        </Alert>
      </Container>
    );
  }

  if (loading) {
    return (
      <Container maxWidth="md" sx={{ mt: 4, textAlign: 'center' }}>
        <CircularProgress />
      </Container>
    );
  }

  if (error || !order) {
    return (
      <Container maxWidth="md" sx={{ mt: 4 }}>
        <Alert severity="error">
          {error || 'Order not found'}
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Box sx={{ textAlign: 'center', mb: 4 }}>
          <CheckCircleIcon color="success" sx={{ fontSize: 60, mb: 2 }} />
          <Typography variant="h4" gutterBottom>
            Order Confirmed!
          </Typography>
          <Typography variant="h6" color="text.secondary">
            Order #{order.order_number}
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mt: 1 }}>
            {new Date(order.created_at).toLocaleString()}
          </Typography>
        </Box>

        <Divider sx={{ my: 3 }} />

        <Typography variant="h6" gutterBottom>
          Order Details
        </Typography>
        <List>
          {order.items.map((item) => (
            <ListItem key={item.id} sx={{ py: 2 }}>
              <ListItemText
                primary={item.name}
                secondary={`Quantity: ${item.quantity}`}
              />
              <Typography variant="body1">
                ${item.subtotal.toFixed(2)}
              </Typography>
            </ListItem>
          ))}
        </List>

        <Divider sx={{ my: 2 }} />

        <Box sx={{ mt: 2 }}>
          <Typography variant="body1" sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <span>Subtotal:</span>
            <span>${(order.total - order.tax).toFixed(2)}</span>
          </Typography>
          <Typography variant="body1" sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <span>Tax:</span>
            <span>${order.tax.toFixed(2)}</span>
          </Typography>
          <Typography variant="h6" sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
            <span>Total:</span>
            <span>${order.total.toFixed(2)}</span>
          </Typography>
        </Box>

        <Box sx={{ mt: 4, display: 'flex', justifyContent: 'center', gap: 2 }}>
          <Button
            variant="contained"
            color="primary"
            onClick={() => navigate('/menu')}
          >
            Continue Shopping
          </Button>
          <Button
            variant="outlined"
            onClick={() => navigate('/review-order')}
          >
            Review Orders
          </Button>
        </Box>
      </Paper>
    </Container>
  );
};

export default OrderConfirmation; 