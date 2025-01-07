import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Switch,
  Tooltip,
} from '@mui/material';
import { Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material';
import { User, UserUpdate } from '../types/user';
import { userService } from '../services/userService';
import UserDialog from '../components/user/UserDialog';
import ConfirmDialog from '../components/common/ConfirmDialog';
import { useSnackbar } from '../contexts/SnackbarContext';

export const UserManagement: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isConfirmDialogOpen, setIsConfirmDialogOpen] = useState(false);
  const [userToDelete, setUserToDelete] = useState<User | null>(null);
  const { showSnackbar } = useSnackbar();

  const loadUsers = async () => {
    try {
      const data = await userService.getUsers();
      setUsers(data);
    } catch (error) {
      showSnackbar('Failed to load users', 'error');
    }
  };

  useEffect(() => {
    loadUsers();
  }, []);

  const handleCreateUser = () => {
    setSelectedUser(null);
    setIsDialogOpen(true);
  };

  const handleEditUser = (user: User) => {
    setSelectedUser(user);
    setIsDialogOpen(true);
  };

  const handleDeleteClick = (user: User) => {
    setUserToDelete(user);
    setIsConfirmDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!userToDelete) return;

    try {
      await userService.deleteUser(userToDelete.id);
      showSnackbar('User deleted successfully', 'success');
      loadUsers();
    } catch (error) {
      showSnackbar('Failed to delete user', 'error');
    }
    setIsConfirmDialogOpen(false);
    setUserToDelete(null);
  };

  const handleToggleActive = async (user: User) => {
    try {
      const updateData = {
        username: user.username,
        email: user.email,
        first_name: user.first_name,
        last_name: user.last_name,
        role: user.role,
        is_active: !user.is_active,
        phone_number: user.phone_number
      };
      await userService.updateUser(user.id, updateData);
      loadUsers();
      showSnackbar('User status updated successfully', 'success');
    } catch (error) {
      showSnackbar('Failed to update user status', 'error');
    }
  };

  const handleSaveUser = async (userData: Partial<User>) => {
    try {
      if (selectedUser) {
        const updateData: UserUpdate = {
          username: userData.username || '',
          email: userData.email || '',
          first_name: userData.first_name || '',
          last_name: userData.last_name || '',
          role: userData.role || 'staff',
          is_active: userData.is_active ?? true,
          phone_number: userData.phone_number || ''
        };
        await userService.updateUser(selectedUser.id, updateData);
        showSnackbar('User updated successfully', 'success');
      } else {
        await userService.createUser(userData as any);
        showSnackbar('User created successfully', 'success');
      }
      setIsDialogOpen(false);
      loadUsers();
    } catch (error) {
      showSnackbar('Failed to save user', 'error');
    }
  };

  const handleUpdateUser = async (userData: Partial<User>) => {
    if (!userData.id) return;
    try {
        const updateData: UserUpdate = {
            username: userData.username,
            email: userData.email,
            first_name: userData.first_name,
            last_name: userData.last_name,
            role: userData.role,
            is_active: userData.is_active
        };
        await userService.updateUser(userData.id, updateData);
        fetchUsers();
    } catch (error) {
        console.error('Error updating user:', error);
    }
  };

  return (
    <Box p={3}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">User Management</Typography>
        <Button
          variant="contained"
          color="primary"
          onClick={handleCreateUser}
        >
          Create User
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Username</TableCell>
              <TableCell>Email</TableCell>
              <TableCell>Role</TableCell>
              <TableCell>Active</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {users.map((user) => (
              <TableRow key={user.id}>
                <TableCell>{`${user.first_name} ${user.last_name}`}</TableCell>
                <TableCell>{user.username}</TableCell>
                <TableCell>{user.email}</TableCell>
                <TableCell>{user.role}</TableCell>
                <TableCell>
                  <Switch
                    checked={user.is_active}
                    onChange={() => handleToggleActive(user)}
                  />
                </TableCell>
                <TableCell>
                  <Tooltip title="Edit">
                    <IconButton onClick={() => handleEditUser(user)}>
                      <EditIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Delete">
                    <IconButton onClick={() => handleDeleteClick(user)}>
                      <DeleteIcon />
                    </IconButton>
                  </Tooltip>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <UserDialog
        open={isDialogOpen}
        user={selectedUser}
        onClose={() => setIsDialogOpen(false)}
        onSave={handleSaveUser}
      />

      <ConfirmDialog
        open={isConfirmDialogOpen}
        title="Delete User"
        content="Are you sure you want to delete this user? This action cannot be undone."
        onConfirm={handleDeleteConfirm}
        onCancel={() => setIsConfirmDialogOpen(false)}
      />
    </Box>
  );
};
