# Restaurant-Ordering-System
Application to setup help customers order food from Restaurants 

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
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   .\venv\Scripts\activate   # Windows
   ```

2. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

3. Run tests:
   ```bash
   pytest
   ```

## Running the Application

1. Start backend server:
   ```bash
   uvicorn backend.api.app:app --reload
   ```

2. Start frontend development server:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

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