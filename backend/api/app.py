import os
os.environ["TESTING"] = os.getenv("TESTING", "0")  # Ensure TESTING is set before imports

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from backend.utils.database import init_db
from backend.api.routes.menu import router as menu_router
from backend.api.routes.cart import router as cart_router
from backend.api.routes.ratings import router as ratings_router
from backend.api.routes.order import router as order_router
from backend.api.routes.users import router as user_router

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
origins = [
    "http://localhost:5173",  # Local development
    "http://localhost:5174",  # Additional dev port
    "http://localhost:3000",  # Local production build
    "https://restaurant-ordering-system-*.vercel.app",  # Vercel preview deployments
    "https://restaurant-ordering-system.vercel.app",  # Vercel production
    "https://restaurant-management-system-5c3x.onrender.com"  # Render deployment
]

# Log the configured origins
logger.debug(f"Configured CORS origins: {origins}")

# Function to validate origin
def validate_origin(origin: str) -> bool:
    if not origin:
        return False
    # Allow localhost
    if origin.startswith(("http://localhost:", "http://127.0.0.1:")):
        return True
    # Allow Vercel preview deployments
    if origin.startswith("https://restaurant-ordering-system-") and origin.endswith(".vercel.app"):
        return True
    # Allow Render deployment
    if origin == "https://restaurant-management-system-5c3x.onrender.com":
        return True
    return False

# Configure CORS - must be added before other middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Using explicit origins list instead of wildcard
    allow_origin_regex=r"https://restaurant-ordering-system.*\.vercel\.app",
    allow_credentials=True,  # Changed to True to allow credentials
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "Accept",
        "Origin",
        "X-Requested-With",
        "X-CSRF-Token",
        "Access-Control-Allow-Origin",
        "Access-Control-Allow-Methods",
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Credentials"  # Added this header
    ],
    expose_headers=["*"],
    max_age=3600,
)

# Mount static files directory
BASE_PATH = os.getenv('STATIC_PATH', os.path.join(os.getcwd(), 'static'))
static_dir = Path(BASE_PATH)
logger.info(f"Using static directory: {static_dir}")

static_dir.mkdir(parents=True, exist_ok=True)
images_dir = static_dir / "images"
images_dir.mkdir(parents=True, exist_ok=True)

# Mount static files with custom configuration
app.mount("/static", StaticFiles(directory=static_dir, html=True), name="static")

# Add middleware to handle static file headers
@app.middleware("http")
async def add_cache_control_header(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/static/") and response.status_code < 400:
        # Cache static files for 1 hour
        response.headers["Cache-Control"] = "public, max-age=3600"
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
    return response

# Add exception handler for better error reporting
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception handler caught: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )

# Include routers
logger.info("Registering API routers...")

# Register user router
logger.debug("Adding user router...")
app.include_router(user_router, prefix="/api")
logger.debug(f"User router routes: {[route.path for route in user_router.routes]}")

# Register menu router
logger.info("Registering menu router...")
app.include_router(menu_router, prefix="/api")
logger.debug(f"Menu router routes: {[route.path for route in menu_router.routes]}")

# Register cart router
logger.info("Registering cart router...")
app.include_router(cart_router, prefix="/api")
logger.debug(f"Cart router routes: {[route.path for route in cart_router.routes]}")

# Register ratings router
logger.info("Registering ratings router...")
app.include_router(ratings_router, prefix="/api")
logger.debug(f"Ratings router routes: {[route.path for route in ratings_router.routes]}")

# Register order router
logger.info("Registering order router...")
app.include_router(order_router, prefix="/api")
logger.debug(f"Order router routes: {[route.path for route in order_router.routes]}")

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
