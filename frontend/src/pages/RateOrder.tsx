import React, { useState } from 'react';
import {
  Container,
  Typography,
  Paper,
  TextField,
  Button,
  Box,
  CircularProgress,
  Alert,
  Rating,
  Stack,
} from '@mui/material';

const RateOrder: React.FC = () => {
  const [orderNumber, setOrderNumber] = useState('');
  const [rating, setRating] = useState<number | null>(null);
  const [comment, setComment] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!rating) {
      setError('Please provide a rating');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // TODO: Implement order rating functionality
      console.log('Rating order:', { orderNumber, rating, comment });
    } catch (err) {
      setError('Failed to submit rating. Please check your order number and try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="sm">
      <Box sx={{ mt: 4 }}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            Rate Order
          </Typography>
          
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <form onSubmit={handleSubmit}>
            <Stack spacing={2}>
              <TextField
                fullWidth
                label="Order Number"
                value={orderNumber}
                onChange={(e) => setOrderNumber(e.target.value)}
                required
                disabled={loading}
              />
              
              <Box>
                <Typography component="legend">Rating</Typography>
                <Rating
                  name="order-rating"
                  value={rating}
                  onChange={(_, newValue) => setRating(newValue)}
                  disabled={loading}
                  size="large"
                />
              </Box>

              <TextField
                fullWidth
                label="Comments"
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                multiline
                rows={4}
                disabled={loading}
              />
              
              <Button
                type="submit"
                variant="contained"
                color="primary"
                fullWidth
                disabled={loading}
              >
                {loading ? <CircularProgress size={24} /> : 'Submit Rating'}
              </Button>
            </Stack>
          </form>
        </Paper>
      </Box>
    </Container>
  );
};

export default RateOrder; 