from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os
from datetime import datetime
from pathlib import Path

from backend.utils.database import init_db
from .routes import menu

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Restaurant Application API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory
static_dir = Path("static")
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include routers with /api prefix
app.include_router(menu.router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    """Initialize the database on startup."""
    init_db()

@app.get("/")
async def root():
    return {"message": "Welcome to Restaurant Application API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": str(datetime.now())}
