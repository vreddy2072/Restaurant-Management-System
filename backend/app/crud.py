from sqlalchemy.orm import Session
from . import models, schemas
import logging

logger = logging.getLogger(__name__)

def update_menu_item(db: Session, item_id: int, item: schemas.MenuItemUpdate):
    logger.info(f"Updating menu item {item_id} with data: {item.dict()}")
    
    db_item = db.query(models.MenuItem).filter(models.MenuItem.id == item_id).first()
    if not db_item:
        logger.warning(f"Menu item {item_id} not found")
        return None
    
    # Update the item data
    item_data = item.dict(exclude_unset=True)
    logger.info(f"Update data after exclude_unset: {item_data}")
    
    # Explicitly handle allergens
    if 'allergens' in item_data:
        allergens = item_data.pop('allergens')  # Remove from dict to avoid double processing
        logger.info(f"Setting allergens to: {allergens}")
        try:
            # Ensure it's a list
            allergens_list = list(allergens) if allergens is not None else []
            db_item.allergens = allergens_list
            logger.info(f"Allergens set to: {db_item.allergens}")
        except Exception as e:
            logger.error(f"Error setting allergens: {str(e)}")
            raise
    
    # Update other fields
    for key, value in item_data.items():
        setattr(db_item, key, value)
    
    try:
        db.commit()
        db.refresh(db_item)
        logger.info(f"Updated item: {db_item.id}")
        logger.info(f"Final allergens value: {db_item.allergens}")
        return db_item
    except Exception as e:
        logger.error(f"Error updating menu item: {str(e)}")
        db.rollback()
        raise 