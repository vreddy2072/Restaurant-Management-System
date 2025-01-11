# Restaurant-Ordering-System
Application for customers to order from restaurants

# Restaurant Application

A full-stack restaurant ordering application with FastAPI backend and React frontend.

## Setup Files

The project uses modern Python packaging tools with these configuration files:

1. `pyproject.toml`: Main project configuration
   - Build system requirements
   - Project metadata
   - Dependencies (runtime and development)
   - Tool configurations (pytest, black, isort)

2. `setup.py`: Package installation
   - Minimal configuration for package discovery
   - Required for complex package structures

## Development Setup

1. Create and activate virtual environment:
   ```bash
   # Create virtual environment without system site packages (important!)
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   .\venv\Scripts\activate   # Windows
   ```

2. Install backend dependencies:
   ```bash
   # Install backend dependencies in development mode
   pip install -e ".[dev]"
   pip install uvicorn

   # Verify installation
   pip list
   ```

3. Install frontend dependencies:
   ```bash
   # Navigate to frontend directory
   cd frontend

   # Install frontend dependencies
   npm install --legacy-peer-deps
   ```

4. Run tests (optional):
   ```bash
   pytest
   ```

5. Set up development environment:
   ```bash
   # Create static directories for file uploads
   mkdir -p static/images

   # Seed the database with initial data
   cd backend
   python scripts/seed_allergens.py
   cd ..
   ```

## Running the Application

### Development Mode

1. Start backend server (from project root):
   ```bash
   # Activate virtual environment if not already activated
   .\venv\Scripts\activate   # Windows
   source venv/bin/activate  # Linux/Mac

   # Start backend server on port 8000
   uvicorn backend.api.app:app --reload
   ```
   The backend will serve the API at http://localhost:8000 and static files (like images) from the /static directory.

2. In a new terminal, start frontend development server:
   ```bash
   # Navigate to frontend directory
   cd frontend

   # Install dependencies (if not already installed)
   npm install --legacy-peer-deps

   # Start frontend development server
   npm run dev
   ```
   The frontend will be available at http://localhost:5173

### Important Notes
- Both servers must be running simultaneously for the application to work properly
- Backend server must run on port 8000 for the frontend to communicate with it correctly
- Static files (images) are served from the backend server, so make sure the backend is running to see menu item images
- The frontend development server (Vite) runs on port 5173 by default

## Database Setup

1. Seed allergens data:
   ```bash
   cd backend
   python scripts/seed_allergens.py
   ```
   This will populate the database with common allergens required for menu item creation.

## Code Quality

The project uses several tools for code quality:
- pytest for testing
- black for code formatting
- isort for import sorting
- mypy for type checking

Run formatting:
```bash
black .
isort .
``` 
