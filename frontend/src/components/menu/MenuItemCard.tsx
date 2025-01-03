import React, { useEffect } from 'react';
import {
  Card,
  CardContent,
  CardMedia,
  Typography,
  IconButton,
  Chip,
  Box,
  Skeleton,
  Rating,
  Tooltip,
  Stack,
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

interface MenuItemCardProps {
  item: MenuItem;
  isLoading?: boolean;
  error?: string;
  onEdit?: (item: MenuItem) => void;
  onDelete?: (item: MenuItem) => void;
  onToggleActive?: (item: MenuItem) => void;
}

const StyledCard = styled(Card)(({ theme }) => ({
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  position: 'relative',
  transition: 'transform 0.2s ease-in-out',
  '&:hover': {
    transform: 'translateY(-4px)',
    boxShadow: theme.shadows[4]
  }
}));

const DietaryBadges = styled(Box)(({ theme }) => ({
  position: 'absolute',
  top: theme.spacing(1),
  right: theme.spacing(1),
  display: 'flex',
  gap: theme.spacing(0.5),
  zIndex: 1
}));

const PriceChip = styled(Chip)(({ theme }) => ({
  position: 'absolute',
  bottom: theme.spacing(1),
  right: theme.spacing(1),
  backgroundColor: theme.palette.primary.main,
  color: theme.palette.primary.contrastText,
  fontWeight: 'bold'
}));

export const MenuItemCard: React.FC<MenuItemCardProps> = ({
  item,
  isLoading = false,
  error,
  onEdit,
  onDelete,
  onToggleActive
}) => {
  if (error) {
    return (
      <StyledCard>
        <CardContent>
          <Typography color="error">{error}</Typography>
        </CardContent>
      </StyledCard>
    );
  }

  const renderDietaryBadges = () => (
    <DietaryBadges>
      {item.is_vegan && (
        <Tooltip title="Vegan">
          <VeganIcon color="success" />
        </Tooltip>
      )}
      {item.is_vegetarian && !item.is_vegan && (
        <Tooltip title="Vegetarian">
          <VegetarianIcon color="success" />
        </Tooltip>
      )}
      {item.is_gluten_free && (
        <Tooltip title="Gluten Free">
          <GlutenFreeIcon color="info" />
        </Tooltip>
      )}
      {item.spice_level > 0 && (
        <Tooltip title={`Spice Level: ${item.spice_level}`}>
          <Stack direction="row">
            {[...Array(item.spice_level)].map((_, index) => (
              <SpicyIcon key={index} color="error" fontSize="small" />
            ))}
          </Stack>
        </Tooltip>
      )}
    </DietaryBadges>
  );

  if (isLoading) {
    return (
      <StyledCard>
        <Skeleton variant="rectangular" height={200} animation="wave" />
        <CardContent>
          <Skeleton variant="text" width="80%" />
          <Skeleton variant="text" width="60%" />
          <Skeleton variant="text" width="40%" />
        </CardContent>
      </StyledCard>
    );
  }

  useEffect(() => {
    console.log('Rendering image URL:', item.image_url);
  }, [item.image_url]);

  return (
    <StyledCard>
      {renderDietaryBadges()}
      <CardMedia
        component="img"
        height="200"
        image={item.image_url || '/default-food-image.jpg'}
        alt={item.name}
        sx={{ objectFit: 'cover' }}
      />
      <CardContent sx={{ flexGrow: 1 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
          <Typography variant="h6" component="h2" noWrap>
            {item.name}
          </Typography>
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
        </Box>
        <Typography variant="body2" color="text.secondary" paragraph>
          {item.description}
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <Rating value={item.average_rating} precision={0.5} readOnly size="small" />
          <Typography variant="body2" color="text.secondary" sx={{ ml: 1 }}>
            ({item.rating_count})
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', mb: 1 }}>
          {item.allergens.map((allergen) => (
            <Chip
              key={allergen.id}
              label={allergen.name}
              size="small"
              variant="outlined"
              color="warning"
              title={allergen.description}
            />
          ))}
        </Box>
        <Typography variant="body2" color="text.secondary">
          Prep time: {item.preparation_time} mins
        </Typography>
      </CardContent>
      <Box sx={{ p: 1, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <IconButton size="small" onClick={() => onEdit?.(item)} color="primary">
            <EditIcon />
          </IconButton>
          <IconButton size="small" onClick={() => onDelete?.(item)} color="error">
            <DeleteIcon />
          </IconButton>
        </Box>
        <PriceChip label={`$${item.price.toFixed(2)}`} />
      </Box>
    </StyledCard>
  );
};