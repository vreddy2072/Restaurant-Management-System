import React from 'react';
import {
  Paper,
  Typography,
  Box,
  Rating,
  Stack,
  Divider,
  Card,
  CardContent,
} from '@mui/material';
import { RestaurantFeedback } from '../../services/feedbackService';

interface Props {
  feedbackList: RestaurantFeedback[];
}

const RecentFeedback: React.FC<Props> = ({ feedbackList }) => {
  return (
    <Paper elevation={3} sx={{ p: 3, maxWidth: 800, mx: 'auto' }}>
      <Typography variant="h5" gutterBottom>
        Recent Feedback
      </Typography>
      <Stack spacing={2} mt={2}>
        {feedbackList.map((feedback) => (
          <Card key={feedback.id}>
            <CardContent>
              <Typography variant="body1" gutterBottom>
                {feedback.feedback_text}
              </Typography>
              <Divider sx={{ my: 1 }} />
              <Stack spacing={1}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Typography component="legend" sx={{ minWidth: 120 }}>
                    Service
                  </Typography>
                  <Rating value={feedback.service_rating} readOnly size="small" />
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Typography component="legend" sx={{ minWidth: 120 }}>
                    Ambiance
                  </Typography>
                  <Rating value={feedback.ambiance_rating} readOnly size="small" />
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Typography component="legend" sx={{ minWidth: 120 }}>
                    Cleanliness
                  </Typography>
                  <Rating value={feedback.cleanliness_rating} readOnly size="small" />
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Typography component="legend" sx={{ minWidth: 120 }}>
                    Value for Money
                  </Typography>
                  <Rating value={feedback.value_rating} readOnly size="small" />
                </Box>
              </Stack>
              <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                Posted on {new Date(feedback.created_at).toLocaleDateString()}
              </Typography>
            </CardContent>
          </Card>
        ))}
        {feedbackList.length === 0 && (
          <Typography variant="body1" color="text.secondary" textAlign="center">
            No feedback available yet
          </Typography>
        )}
      </Stack>
    </Paper>
  );
};

export default RecentFeedback; 