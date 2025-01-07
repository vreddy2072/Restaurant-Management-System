import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Switch,
  Box,
} from '@mui/material';
import { User, UserRole } from '../../types/user';

interface UserDialogProps {
  open: boolean;
  user: User | null;
  onClose: () => void;
  onSave: (data: Partial<User>) => Promise<void>;
}

const UserDialog: React.FC<UserDialogProps> = ({
  open,
  user,
  onClose,
  onSave,
}) => {
  const [formData, setFormData] = useState<Partial<User>>({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    role: 'staff',
    is_active: true,
    phone_number: '',
  });
  const [password, setPassword] = useState('');

  useEffect(() => {
    if (user) {
      setFormData({
        username: user.username,
        email: user.email,
        first_name: user.first_name,
        last_name: user.last_name,
        role: user.role,
        is_active: user.is_active,
        phone_number: user.phone_number || '',
      });
      setPassword('');
    } else {
      setFormData({
        username: '',
        email: '',
        first_name: '',
        last_name: '',
        role: 'staff',
        is_active: true,
        phone_number: '',
      });
      setPassword('');
    }
  }, [user]);

  const handleChange = (field: keyof User) => (
    event: React.ChangeEvent<HTMLInputElement | { value: unknown }>
  ) => {
    setFormData({
      ...formData,
      [field]: event.target.value,
    });
  };

  const handleRoleChange = (event: SelectChangeEvent<string>) => {
    const role = event.target.value as UserRole;
    setFormData(prev => ({ ...prev, role }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const userData = { ...formData };
    if (password) {
      (userData as any).password = password;
    }
    await onSave(userData);
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <form onSubmit={handleSubmit}>
        <DialogTitle>{user ? 'Edit User' : 'Create User'}</DialogTitle>
        <DialogContent>
          <Box display="grid" gap={2} py={2}>
            <TextField
              label="Username"
              value={formData.username}
              onChange={handleChange('username')}
              required
              fullWidth
            />
            <TextField
              label="Email"
              type="email"
              value={formData.email}
              onChange={handleChange('email')}
              required
              fullWidth
            />
            <TextField
              label="Password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required={!user}
              fullWidth
            />
            <TextField
              label="First Name"
              value={formData.first_name}
              onChange={handleChange('first_name')}
              required
              fullWidth
            />
            <TextField
              label="Last Name"
              value={formData.last_name}
              onChange={handleChange('last_name')}
              required
              fullWidth
            />
            <FormControl fullWidth required>
              <InputLabel>Role</InputLabel>
              <Select
                value={formData.role}
                onChange={handleRoleChange}
                label="Role"
              >
                <MenuItem value="admin">Admin</MenuItem>
                <MenuItem value="manager">Manager</MenuItem>
                <MenuItem value="staff">Staff</MenuItem>
                <MenuItem value="customer">Customer</MenuItem>
              </Select>
            </FormControl>
            <TextField
              label="Phone Number"
              value={formData.phone_number}
              onChange={handleChange('phone_number')}
              fullWidth
            />
            <FormControlLabel
              control={
                <Switch
                  checked={formData.is_active}
                  onChange={(e) =>
                    setFormData({ ...formData, is_active: e.target.checked })
                  }
                />
              }
              label="Active"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>Cancel</Button>
          <Button type="submit" variant="contained" color="primary">
            {user ? 'Save' : 'Create'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default UserDialog;
