import React from 'react';
import { Snackbar, Alert, AlertColor } from '@mui/material';

export interface ToastProps {
  open: boolean;
  onClose: () => void;
  message: string;
  severity?: AlertColor;
}

const Toast: React.FC<ToastProps> = ({
  open,
  onClose,
  message,
  severity = 'success'
}) => {
  return (
    <Snackbar
      open={open}
      autoHideDuration={6000}
      onClose={onClose}
      anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
    >
      <Alert onClose={onClose} severity={severity} sx={{ width: '100%' }}>
        {message}
      </Alert>
    </Snackbar>
  );
};

export default Toast; 