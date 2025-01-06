import React, { useState } from 'react';
import {
  Box,
  Button,
  TextField,
  Rating,
  Typography,
  Paper,
  Stack,
  Alert,
} from '@mui/material';
import { RestaurantFeedbackCreate } from '../../services/feedbackService';

interface Props {
  onSubmit: (feedback: RestaurantFeedbackCreate) => Promise<void>;
}

const RestaurantFeedbackForm: React.FC<Props> = ({ onSubmit }) => {
  const [feedback, setFeedback] = useState<RestaurantFeedbackCreate>({
    feedback_text: '',
    service_rating: 0,
    ambiance_rating: 0,
    cleanliness_rating: 0,
    value_rating: 0,
  });
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState<string>('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    try {
      if (!feedback.feedback_text.trim()) {
        throw new Error('Please provide feedback text');
      }
      if (feedback.service_rating === 0 || 
          feedback.ambiance_rating === 0 || 
          feedback.cleanliness_rating === 0 || 
          feedback.value_rating === 0) {
        throw new Error('Please provide all ratings');
      }

      await onSubmit(feedback);
      setSuccess('Thank you for your feedback!');
      setFeedback({
        feedback_text: '',
        service_rating: 0,
        ambiance_rating: 0,
        cleanliness_rating: 0,
        value_rating: 0,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit feedback');
    }
  };

  return (
    <Paper elevation={3} sx={{ p: 3, maxWidth: 600, mx: 'auto' }}>
      <Typography variant="h5" gutterBottom>
        Restaurant Feedback Form
      </Typography>
      <form onSubmit={handleSubmit}>
        <Stack spacing={3}>
          {error && <Alert severity="error">{error}</Alert>}
          {success && <Alert severity="success">{success}</Alert>}

          <Box>
            <Typography component="legend">Service Rating</Typography>
            <Rating
              value={feedback.service_rating}
              onChange={(_, value) => setFeedback(prev => ({ ...prev, service_rating: value || 0 }))}
            />
          </Box>

          <Box>
            <Typography component="legend">Ambiance Rating</Typography>
            <Rating
              value={feedback.ambiance_rating}
              onChange={(_, value) => setFeedback(prev => ({ ...prev, ambiance_rating: value || 0 }))}
            />
          </Box>

          <Box>
            <Typography component="legend">Cleanliness Rating</Typography>
            <Rating
              value={feedback.cleanliness_rating}
              onChange={(_, value) => setFeedback(prev => ({ ...prev, cleanliness_rating: value || 0 }))}
            />
          </Box>

          <Box>
            <Typography component="legend">Value for Money Rating</Typography>
            <Rating
              value={feedback.value_rating}
              onChange={(_, value) => setFeedback(prev => ({ ...prev, value_rating: value || 0 }))}
            />
          </Box>

          <TextField
            label="Your Feedback"
            multiline
            rows={4}
            value={feedback.feedback_text}
            onChange={(e) => setFeedback(prev => ({ ...prev, feedback_text: e.target.value }))}
            fullWidth
            required
          />

          <Button type="submit" variant="contained" color="primary">
            Submit Feedback
          </Button>
        </Stack>
      </form>
    </Paper>
  );
};

export default RestaurantFeedbackForm; 