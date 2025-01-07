import React, { useEffect, useState } from 'react';
import { Container, Grid, Box } from '@mui/material';
import RestaurantFeedbackForm from '../components/feedback/RestaurantFeedbackForm';
import FeedbackStats from '../components/feedback/FeedbackStats';
import RecentFeedback from '../components/feedback/RecentFeedback';
import feedbackService, {
  RestaurantFeedback,
  RestaurantFeedbackStats,
  RestaurantFeedbackCreate,
} from '../services/feedbackService';
import { useAuth } from '../contexts/AuthContext';

const FeedbackPage: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const [stats, setStats] = useState<RestaurantFeedbackStats>({
    average_service_rating: 0,
    average_ambiance_rating: 0,
    average_cleanliness_rating: 0,
    average_value_rating: 0,
    total_reviews: 0,
  });
  const [recentFeedback, setRecentFeedback] = useState<RestaurantFeedback[]>([]);

  const fetchData = async () => {
    try {
      const [statsData, recentData] = await Promise.all([
        feedbackService.getRestaurantFeedbackStats(),
        feedbackService.getRecentRestaurantFeedback(),
      ]);
      setStats(statsData);
      setRecentFeedback(recentData);
    } catch (error) {
      console.error('Failed to fetch feedback data:', error);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleSubmitFeedback = async (feedback: RestaurantFeedbackCreate) => {
    try {
      await feedbackService.createRestaurantFeedback(feedback);
      await fetchData(); // Refresh data after submission
    } catch (error) {
      console.error('Failed to submit feedback:', error);
      throw error;
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Grid container spacing={4}>
        <Grid item xs={12} md={6}>
          {isAuthenticated && (
            <RestaurantFeedbackForm onSubmit={handleSubmitFeedback} />
          )}
        </Grid>
        <Grid item xs={12} md={6}>
          <FeedbackStats stats={stats} />
        </Grid>
      </Grid>
    </Container>
  );
};

export default FeedbackPage; 