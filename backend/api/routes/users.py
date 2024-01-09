from fastapi import APIRouter, Depends, HTTPException, status, Form, Request
from sqlalchemy.orm import Session
from typing import List
import logging

from backend.models.schemas.user import UserCreate, UserUpdate, UserResponse, UserLogin
from backend.services.user_service import UserService
from backend.utils.database import get_db
from backend.utils.auth import create_access_token, get_current_user

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["users"])
async def register_user(request: Request, user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        # Log request details
        body = await request.json()
        logger.debug(f"Received registration request: {body}")
        logger.debug(f"Request headers: {request.headers}")
        
        service = UserService(db)
        user = service.create_user(user_data)
        logger.info(f"User created successfully: {user.to_dict()}")
        return user
    except ValueError as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error during registration: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

@router.post("/login", tags=["users"])
async def login_user(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    """Authenticate a user and return a token"""
    try:
        logger.debug(f"Login attempt for email: {email}")
        service = UserService(db)
        user = service.authenticate_user(email, password)
        if not user:
            logger.warning(f"Failed login attempt for email: {email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Create access token
        token = create_access_token(data={"sub": user.email})
        logger.info(f"Successful login for user: {email}")
        return {"access_token": token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during login"
        )

@router.post("/guest-login", tags=["users"])
async def guest_login(request: Request, db: Session = Depends(get_db)):
    """Create and login as a guest user"""
    try:
        logger.debug("Guest login attempt")
        service = UserService(db)
        guest_user, password = service.authenticate_guest()
        
        # Create access token
        token = create_access_token(data={"sub": guest_user.email})
        logger.info(f"Successful guest login: {guest_user.email}")
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": guest_user,
            "temp_password": password  # Only for guest users to enable immediate access
        }
    except Exception as e:
        logger.error(f"Guest login error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during guest login"
        )

@router.get("/me", response_model=UserResponse, tags=["users"])
async def get_me(current_user: UserResponse = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@router.put("/me", response_model=UserResponse, tags=["users"])
async def update_user_info(
    user_update: UserUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update the current user's information"""
    try:
        service = UserService(db)
        updated_user = service.update_user(current_user.id, user_update)
        logger.info(f"User {current_user.id} updated successfully")
        return updated_user
    except ValueError as e:
        logger.error(f"Update error for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT, tags=["users"])
async def deactivate_account(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deactivate the current user's account"""
    try:
        service = UserService(db)
        service.deactivate_user(current_user.id)
        logger.info(f"User {current_user.id} deactivated successfully")
    except Exception as e:
        logger.error(f"Error deactivating user {current_user.id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while deactivating account"
        )
