import React, { useState, useEffect } from 'react';
import {
  Box,
  Rating,
  Typography,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Snackbar,
  Alert,
  Stack
} from '@mui/material';
import { Star as StarIcon } from '@mui/icons-material';
import { ratingService, RatingAverage } from '../../services/ratingService';
import { useAuth } from '../../contexts/AuthContext';

interface RatingComponentProps {
  menuItemId: number;
  initialRating?: number;
  onRatingChange?: (newRating: number) => void;
}

const RatingComponent: React.FC<RatingComponentProps> = ({
  menuItemId,
  initialRating = 0,
  onRatingChange
}) => {
  const { user } = useAuth();
  const [rating, setRating] = useState<number | null>(null);
  const [averageRating, setAverageRating] = useState<RatingAverage>({ average: 0, total: 0 });
  const [hover, setHover] = useState(-1);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [comment, setComment] = useState('');
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [severity, setSeverity] = useState<'success' | 'error'>('success');

  // Load average rating
  useEffect(() => {
    const loadAverageRating = async () => {
      const average = await ratingService.getAverageRating(menuItemId);
      setAverageRating(average);
    };
    loadAverageRating();
  }, [menuItemId]);

  // Load user rating
  useEffect(() => {
    const loadUserRating = async () => {
      try {
        const userRating = await ratingService.getUserRating(menuItemId);
        if (userRating) {
          setRating(userRating.rating);
          setComment(userRating.comment || '');
        } else {
          setRating(null);
          setComment('');
        }
      } catch (error) {
        console.error('Error loading user rating:', error);
      }
    };

    if (user) {
      loadUserRating();
    }
  }, [menuItemId, user]);

  const handleRatingClick = (newValue: number | null) => {
    if (!user) {
      setSnackbarMessage('Please login to rate items');
      setSeverity('error');
      setSnackbarOpen(true);
      return;
    }
    const roundedValue = newValue ? Math.round(newValue) : null;
    setRating(roundedValue);
    setDialogOpen(true);
  };

  const handleSubmitRating = async () => {
    try {
      if (rating !== null) {
        const validRating = Math.max(1, Math.min(5, Math.round(rating)));
        await ratingService.createOrUpdateRating(menuItemId, validRating, comment);
        // Refresh average rating after submitting
        const newAverage = await ratingService.getAverageRating(menuItemId);
        setAverageRating(newAverage);
        setSnackbarMessage('Rating submitted successfully');
        setSeverity('success');
        setSnackbarOpen(true);
        if (onRatingChange) {
          onRatingChange(validRating);
        }
      }
    } catch (error) {
      console.error('Error submitting rating:', error);
      setSnackbarMessage('Error submitting rating. Please try again.');
      setSeverity('error');
      setSnackbarOpen(true);
    }
    setDialogOpen(false);
  };

  return (
    <>
      <Stack spacing={1}>
        {/* Average Rating Display */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Rating
            value={averageRating.average}
            precision={0.1}
            readOnly
            size="small"
          />
          <Typography variant="body2" color="text.secondary">
            {`${averageRating.average.toFixed(1)} (${averageRating.total} ${
              averageRating.total === 1 ? 'rating' : 'ratings'
            })`}
          </Typography>
        </Box>

        {/* User Rating Input */}
        {user && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Rating
              value={rating || 0}
              precision={1}
              onChange={(_, newValue) => handleRatingClick(newValue)}
              onChangeActive={(_, newHover) => setHover(newHover)}
              emptyIcon={<StarIcon style={{ opacity: 0.55 }} fontSize="inherit" />}
            />
            <Typography variant="body2" color="text.secondary">
              {hover !== -1 ? hover : rating || 0}
            </Typography>
          </Box>
        )}
      </Stack>

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)}>
        <DialogTitle>Rate this item</DialogTitle>
        <DialogContent>
          <Box sx={{ py: 2 }}>
            <Rating
              value={rating}
              onChange={(_, newValue) => setRating(newValue ? Math.round(newValue) : null)}
              size="large"
              precision={1}
            />
          </Box>
          <TextField
            fullWidth
            multiline
            rows={3}
            variant="outlined"
            label="Comment (optional)"
            value={comment}
            onChange={(e) => setComment(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleSubmitRating} variant="contained">
            Submit
          </Button>
        </DialogActions>
      </Dialog>

      <Snackbar
        open={snackbarOpen}
        autoHideDuration={4000}
        onClose={() => setSnackbarOpen(false)}
      >
        <Alert
          onClose={() => setSnackbarOpen(false)}
          severity={severity}
          variant="filled"
        >
          {snackbarMessage}
        </Alert>
      </Snackbar>
    </>
  );
};

export default RatingComponent; 