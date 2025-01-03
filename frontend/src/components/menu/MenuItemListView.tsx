import React from 'react';
import {
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  ListItemSecondaryAction,
  Avatar,
  Typography,
  IconButton,
  Tooltip,
  Chip,
  Stack,
  Box,
  Switch,
  FormControlLabel
} from '@mui/material';
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  EmojiNature as VeganIcon,
  Grass as VegetarianIcon,
  NoMeals as GlutenFreeIcon,
  LocalFireDepartment as SpicyIcon
} from '@mui/icons-material';
import type { MenuItem } from '../../types/menu';
import { styled } from '@mui/material/styles';

interface MenuItemListViewProps {
  item: MenuItem;
  onEdit?: (item: MenuItem) => void;
  onDelete?: (item: MenuItem) => void;
  onToggleActive?: (item: MenuItem) => void;
}

const StyledListItem = styled(ListItem)(({ theme }) => ({
  marginBottom: theme.spacing(1),
  backgroundColor: theme.palette.background.paper,
  borderRadius: theme.shape.borderRadius,
  '&:hover': {
    backgroundColor: theme.palette.action.hover,
  }
}));

const DietaryIcons = styled(Stack)(({ theme }) => ({
  flexDirection: 'row',
  gap: theme.spacing(0.5),
  alignItems: 'center'
}));

const PriceChip = styled(Chip)(({ theme }) => ({
  backgroundColor: theme.palette.primary.main,
  color: theme.palette.primary.contrastText,
  fontWeight: 'bold',
  marginLeft: theme.spacing(1)
}));

export const MenuItemListView: React.FC<MenuItemListViewProps> = ({
  item,
  onEdit,
  onDelete,
  onToggleActive
}) => {
  const renderDietaryIcons = () => (
    <DietaryIcons>
      {item.is_vegan && (
        <Tooltip title="Vegan">
          <VeganIcon color="success" fontSize="small" />
        </Tooltip>
      )}
      {item.is_vegetarian && !item.is_vegan && (
        <Tooltip title="Vegetarian">
          <VegetarianIcon color="success" fontSize="small" />
        </Tooltip>
      )}
      {item.is_gluten_free && (
        <Tooltip title="Gluten Free">
          <GlutenFreeIcon color="info" fontSize="small" />
        </Tooltip>
      )}
      {item.spice_level > 0 && (
        <Stack direction="row">
          {[...Array(item.spice_level)].map((_, index) => (
            <SpicyIcon
              key={index}
              color="error"
              fontSize="small"
            />
          ))}
        </Stack>
      )}
    </DietaryIcons>
  );

  return (
    <StyledListItem
      secondaryAction={
        <Stack direction="row" spacing={1} alignItems="center">
          <FormControlLabel
            control={
              <Switch
                checked={item.is_active}
                onChange={() => onToggleActive?.(item)}
                color="primary"
                size="small"
              />
            }
            label={item.is_active ? "Active" : "Inactive"}
            labelPlacement="start"
          />
          {onEdit && (
            <IconButton
              edge="end"
              aria-label="edit"
              onClick={() => onEdit(item)}
              size="small"
            >
              <EditIcon />
            </IconButton>
          )}
          {onDelete && (
            <IconButton
              edge="end"
              aria-label="delete"
              onClick={() => onDelete(item)}
              size="small"
              color="error"
            >
              <DeleteIcon />
            </IconButton>
          )}
        </Stack>
      }
    >
      <ListItemAvatar>
        <Avatar
          variant="rounded"
          src={item.image_url}
          alt={item.name}
          sx={{ width: 60, height: 60 }}
        />
      </ListItemAvatar>
      <ListItemText
        primary={
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Typography variant="h6" component="div">
              {item.name}
            </Typography>
            <PriceChip
              label={`$${item.price.toFixed(2)}`}
              size="small"
            />
          </Box>
        }
        secondary={
          <Box component="div">
            <Typography variant="body2" color="text.secondary" component="div" gutterBottom>
              {item.description}
            </Typography>
            {renderDietaryIcons()}
          </Box>
        }
      />
    </StyledListItem>
  );
};
