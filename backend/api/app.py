import os
os.environ["TESTING"] = os.getenv("TESTING", "0")  # Ensure TESTING is set before imports

from fastapi import FastAPI, Request, Depends, HTTPException, status, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from backend.utils.database import init_db, get_db
from backend.models.schemas.user import UserCreate, UserUpdate, UserResponse, UserLogin
from backend.services.user_service import UserService
from backend.utils.auth import create_access_token, get_current_user
from backend.api.routes.menu import router as menu_router
from backend.api.routes.cart import router as cart_router
from backend.api.routes.ratings import router as ratings_router

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Restaurant Application API",
    description="API for Restaurant Management System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS with more explicit settings
origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
logger.debug(f"Configured CORS origins: {origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if os.getenv("ENVIRONMENT") == "development" else origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Mount static files directory
static_dir = Path("static")
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Add exception handler for better error reporting
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception handler caught: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )

# Create API router for user endpoints
from fastapi import APIRouter
user_router = APIRouter(prefix="/api/users", tags=["users"])

@user_router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        logger.debug(f"Received registration request: {user_data}")
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

@user_router.post("/login", response_model=dict)
async def login_user(
    user_login: UserLogin,
    db: Session = Depends(get_db)
):
    """Authenticate a user and return a token"""
    try:
        logger.debug(f"Login attempt for email: {user_login.email}")  
        service = UserService(db)
        user = service.authenticate_user(user_login.email, user_login.password)  
        if not user:
            logger.warning(f"Failed login attempt for email: {user_login.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Create access token
        token = create_access_token(data={"sub": user.email})
        logger.info(f"Successful login for user: {user_login.email}")
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": user.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during login"
        )

@user_router.post("/guest-login", tags=["users"])
async def guest_login(request: Request, db: Session = Depends(get_db)):
    """Create and login as a guest user"""
    try:
        logger.debug("Guest login attempt")
        service = UserService(db)
        guest_user, password = service.authenticate_guest()
        
        # Create access token
        token = create_access_token(data={"sub": guest_user.email})
        logger.info(f"Successful guest login: {guest_user.email}")
        
        # Convert user data to dictionary and ensure all required fields are present
        user_dict = guest_user.to_dict()
        logger.debug(f"Guest user data before response: {user_dict}")  
        
        # Ensure required fields are present
        required_fields = ["id", "username", "email", "first_name", "last_name", "role", 
                         "is_active", "is_guest", "is_admin"]
        missing_fields = [field for field in required_fields if field not in user_dict]
        if missing_fields:
            logger.error(f"Missing required fields in user data: {missing_fields}")
            raise ValueError(f"User data missing required fields: {missing_fields}")
        
        response_data = {
            "access_token": token,
            "token_type": "bearer",
            "user": user_dict
        }
        logger.debug(f"Full response data: {response_data}")
        
        return response_data
    except ValueError as e:
        logger.error(f"Guest login validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Guest login error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during guest login: {str(e)}"
        )

@user_router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: UserResponse = Depends(get_current_user)):
    """Get information about the currently logged-in user"""
    return current_user

@user_router.put("/me", response_model=UserResponse)
def update_user_info(
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

@user_router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_account(
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

# Include routers
logger.info("Registering API routers...")

# Register user router
logger.debug("Adding user router...")
app.include_router(user_router)
logger.debug(f"User router routes: {[route.path for route in user_router.routes]}")

# Register menu router
logger.info("Registering menu router...")
app.include_router(menu_router)
logger.debug(f"Menu router routes: {[route.path for route in menu_router.routes]}")

# Register cart router
logger.info("Registering cart router...")
app.include_router(cart_router)
logger.debug(f"Cart router routes: {[route.path for route in cart_router.routes]}")

# Register ratings router
logger.info("Registering ratings router...")
app.include_router(ratings_router)
logger.debug(f"Ratings router routes: {[route.path for route in ratings_router.routes]}")

@app.get("/test", tags=["test"])
def test_endpoint():
    """Test endpoint to verify routing"""
    return {"message": "Test endpoint works!"}

@app.on_event("startup")
async def startup_event():
    """Initialize the database on startup."""
    logger.info("Starting application...")
    init_db()
    logger.info("Database initialized")
    
    # Log all registered routes
    logger.info("Available routes:")
    for route in app.routes:
        if hasattr(route, "methods"):  # Only log routes with HTTP methods
            logger.info(f"{route.methods} {route.path}")
        elif hasattr(route, "path"):    # For other routes like mounted static files
            logger.info(f"Mount: {route.path}")

@app.get("/", tags=["system"])
def root():
    """Root endpoint that lists all available routes"""
    routes = []
    for route in app.routes:
        if hasattr(route, "methods"):
            routes.append({
                "path": route.path,
                "methods": list(route.methods) if route.methods else [],
                "name": route.name,
                "endpoint": route.endpoint.__name__ if route.endpoint else None
            })
    return {
        "message": "Welcome to Restaurant Application API",
        "available_routes": routes,
        "total_routes": len(routes)
    }

@app.get("/health", tags=["system"])
def health_check():
    return {"status": "healthy", "timestamp": str(datetime.now())}
