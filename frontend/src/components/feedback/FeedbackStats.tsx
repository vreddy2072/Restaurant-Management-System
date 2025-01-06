import React from 'react';
import {
  Paper,
  Typography,
  Box,
  Rating,
  Grid,
  Divider,
} from '@mui/material';
import { RestaurantFeedbackStats } from '../../services/feedbackService';

interface Props {
  stats: RestaurantFeedbackStats;
}

const FeedbackStats: React.FC<Props> = ({ stats }) => {
  const ratingCategories = [
    { label: 'Service', value: stats.average_service_rating },
    { label: 'Ambiance', value: stats.average_ambiance_rating },
    { label: 'Cleanliness', value: stats.average_cleanliness_rating },
    { label: 'Value for Money', value: stats.average_value_rating },
  ];

  return (
    <Paper elevation={3} sx={{ p: 3, maxWidth: 600, mx: 'auto' }}>
      <Typography variant="h5" gutterBottom>
        Overall Restaurant Ratings
      </Typography>
      <Typography variant="subtitle1" color="text.secondary" gutterBottom>
        Based on {stats.total_reviews} reviews
      </Typography>
      <Divider sx={{ my: 2 }} />
      <Grid container spacing={2}>
        {ratingCategories.map((category) => (
          <Grid item xs={12} key={category.label}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Typography component="legend" sx={{ minWidth: 120 }}>
                {category.label}
              </Typography>
              <Rating
                value={category.value}
                precision={0.1}
                readOnly
              />
              <Typography variant="body2" color="text.secondary">
                ({category.value.toFixed(1)})
              </Typography>
            </Box>
          </Grid>
        ))}
      </Grid>
    </Paper>
  );
};

export default FeedbackStats; 