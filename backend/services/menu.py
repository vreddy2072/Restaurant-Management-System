from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from ..models.orm.menu import Category, MenuItem, Allergen
from ..models.schemas.menu import CategoryCreate, CategoryUpdate, MenuItemCreate, MenuItemUpdate, AllergenCreate, AllergenUpdate, MenuItemFilters

class MenuService:
    @staticmethod
    def create_category(db: Session, category: CategoryCreate) -> Category:
        db_category = Category(**category.model_dump())
        db.add(db_category)
        try:
            db.commit()
            db.refresh(db_category)
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with name {category.name} already exists"
            )
        return db_category

    @staticmethod
    def get_category(db: Session, category_id: int) -> Category:
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id {category_id} not found"
            )
        return category

    @staticmethod
    def get_categories(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = True
    ) -> List[Category]:
        query = db.query(Category)
        if active_only:
            query = query.filter(Category.is_active == True)
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def update_category(
        db: Session,
        category_id: int,
        category_update: CategoryUpdate
    ) -> Category:
        db_category = MenuService.get_category(db, category_id)
        update_data = category_update.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_category, field, value)
        
        try:
            db.commit()
            db.refresh(db_category)
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        return db_category

    @staticmethod
    def delete_category(db: Session, category_id: int) -> None:
        db_category = MenuService.get_category(db, category_id)
        db_category.is_active = False
        db.commit()

    @staticmethod
    def create_menu_item(db: Session, menu_item: MenuItemCreate) -> MenuItem:
        # Verify category exists
        MenuService.get_category(db, menu_item.category_id)
        
        # Extract allergen_ids and remove from model_dump
        menu_item_data = menu_item.model_dump()
        allergen_ids = menu_item_data.pop('allergen_ids', None)
        
        # Create menu item
        db_menu_item = MenuItem(**menu_item_data)
        
        # Add allergens if specified
        if allergen_ids:
            allergens = []
            for allergen_id in allergen_ids:
                allergen = MenuService.get_allergen(db, allergen_id)
                allergens.append(allergen)
            db_menu_item.allergens = allergens
        
        db.add(db_menu_item)
        try:
            db.commit()
            db.refresh(db_menu_item)
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        return db_menu_item

    @staticmethod
    def get_menu_item(db: Session, item_id: int) -> MenuItem:
        menu_item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
        if not menu_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Menu item with id {item_id} not found"
            )
        return menu_item

    @staticmethod
    def get_menu_items(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        category_id: Optional[int] = None,
        active_only: bool = True
    ) -> List[MenuItem]:
        query = db.query(MenuItem)
        
        if category_id:
            query = query.filter(MenuItem.category_id == category_id)
        
        if active_only:
            query = query.filter(MenuItem.is_active == True)
        
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def update_menu_item(db: Session, menu_item_id: int, menu_item: MenuItemUpdate) -> Optional[MenuItem]:
        db_menu_item = MenuService.get_menu_item(db, menu_item_id)
        if db_menu_item:
            # Get allergen_ids before excluding them
            allergen_ids = menu_item.allergen_ids
            update_data = menu_item.model_dump(exclude_unset=True, exclude={'allergen_ids'})
            
            if 'category_id' in update_data:
                # Verify new category exists
                MenuService.get_category(db, update_data['category_id'])
            
            # Handle allergen_ids separately
            if allergen_ids is not None:
                allergens = []
                for allergen_id in allergen_ids:
                    allergen = MenuService.get_allergen(db, allergen_id)
                    allergens.append(allergen)
                db_menu_item.allergens = allergens
            
            for field, value in update_data.items():
                setattr(db_menu_item, field, value)
            
            try:
                db.commit()
                db.refresh(db_menu_item)
                return db_menu_item
            except Exception as e:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=str(e)
                )

    @staticmethod
    def delete_menu_item(db: Session, item_id: int) -> None:
        db_menu_item = MenuService.get_menu_item(db, item_id)
        db_menu_item.is_active = False
        db.commit()

    @staticmethod
    def get_full_menu(db: Session, active_only: bool = True) -> List[Category]:
        query = db.query(Category)
        if active_only:
            query = query.filter(Category.is_active == True)
        return query.all()

    @staticmethod
    def create_allergen(db: Session, allergen: AllergenCreate) -> Allergen:
        """Create a new allergen."""
        db_allergen = Allergen(**allergen.model_dump())
        db.add(db_allergen)
        try:
            db.commit()
            db.refresh(db_allergen)
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Allergen with name {allergen.name} already exists"
            )
        return db_allergen

    @staticmethod
    def get_allergen(db: Session, allergen_id: int) -> Allergen:
        """Get a specific allergen by ID."""
        allergen = db.query(Allergen).filter(Allergen.id == allergen_id).first()
        if not allergen:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Allergen with id {allergen_id} not found"
            )
        return allergen

    @staticmethod
    def get_allergens(db: Session, skip: int = 0, limit: int = 100) -> List[Allergen]:
        """Get a list of allergens."""
        return db.query(Allergen).offset(skip).limit(limit).all()

    @staticmethod
    def update_allergen(db: Session, allergen_id: int, allergen: AllergenUpdate) -> Allergen:
        """Update an allergen."""
        db_allergen = MenuService.get_allergen(db, allergen_id)
        update_data = allergen.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_allergen, field, value)
        
        try:
            db.commit()
            db.refresh(db_allergen)
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        return db_allergen

    @staticmethod
    def delete_allergen(db: Session, allergen_id: int) -> bool:
        """Delete an allergen."""
        db_allergen = MenuService.get_allergen(db, allergen_id)
        db.delete(db_allergen)
        db.commit()
        return True 

    @staticmethod
    def get_filtered_menu_items(
        db: Session,
        filters: MenuItemFilters,
        skip: int = 0,
        limit: int = 100
    ) -> List[MenuItem]:
        query = db.query(MenuItem)
        
        # Apply filters
        if filters.category_id is not None:
            query = query.filter(MenuItem.category_id == filters.category_id)
        if filters.is_vegetarian is not None:
            query = query.filter(MenuItem.is_vegetarian == filters.is_vegetarian)
        if filters.is_vegan is not None:
            query = query.filter(MenuItem.is_vegan == filters.is_vegan)
        if filters.is_gluten_free is not None:
            query = query.filter(MenuItem.is_gluten_free == filters.is_gluten_free)
        if filters.min_price is not None:
            query = query.filter(MenuItem.price >= filters.min_price)
        if filters.max_price is not None:
            query = query.filter(MenuItem.price <= filters.max_price)
        if filters.min_rating is not None:
            query = query.filter(MenuItem.average_rating >= filters.min_rating)
        if filters.allergen_exclude_ids:
            # Exclude items that have any of the specified allergens
            query = query.filter(~MenuItem.allergens.any(Allergen.id.in_(filters.allergen_exclude_ids)))
        
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def filter_menu_items(
        db: Session,
        is_vegetarian: Optional[bool] = None,
        is_vegan: Optional[bool] = None,
        is_gluten_free: Optional[bool] = None,
        allergen_exclude_ids: Optional[List[int]] = None
    ) -> List[MenuItem]:
        """Filter menu items by dietary preferences and allergens"""
        query = db.query(MenuItem).filter(MenuItem.is_active == True)
        
        if is_vegetarian is not None:
            query = query.filter(MenuItem.is_vegetarian == is_vegetarian)
        
        if is_vegan is not None:
            query = query.filter(MenuItem.is_vegan == is_vegan)
        
        if is_gluten_free is not None:
            query = query.filter(MenuItem.is_gluten_free == is_gluten_free)
        
        if allergen_exclude_ids:
            # Exclude items that contain any of the specified allergens
            for allergen_id in allergen_exclude_ids:
                query = query.filter(~MenuItem.allergens.any(Allergen.id == allergen_id))
        
        return query.all()