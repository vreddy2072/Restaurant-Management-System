# Setup script for Restaurant Application

# Function to check if a command exists
function Test-Command {
    param($Command)
    $oldPreference = $ErrorActionPreference
    $ErrorActionPreference = 'stop'
    try {
        if (Get-Command $Command) { return $true }
    } catch {
        return $false
    }
    finally {
        $ErrorActionPreference = $oldPreference
    }
}

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Blue

# Check Python
if (-not (Test-Command python)) {
    Write-Host "Python is not installed. Please install Python 3.9 or higher." -ForegroundColor Red
    exit 1
}

# Check Node.js
if (-not (Test-Command node)) {
    Write-Host "Node.js is not installed. Please install Node.js 18 or higher." -ForegroundColor Red
    exit 1
}

# Check npm
if (-not (Test-Command npm)) {
    Write-Host "npm is not installed. Please install Node.js with npm." -ForegroundColor Red
    exit 1
}

# Create and activate virtual environment
Write-Host "Setting up Python virtual environment..." -ForegroundColor Blue
if (Test-Path venv) {
    Write-Host "Removing existing virtual environment..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force venv
}
python -m venv venv
.\venv\Scripts\Activate

# Upgrade pip and install build tools
Write-Host "Upgrading pip and installing build tools..." -ForegroundColor Blue
python -m pip install --upgrade pip wheel setuptools

# Install the package in development mode
Write-Host "Installing Python dependencies..." -ForegroundColor Blue
python -m pip install -e ".[dev]"

# Create backend directories if they don't exist
Write-Host "Creating backend directory structure..." -ForegroundColor Blue
$backendDirs = @(
    "backend/api/routes",
    "backend/models/orm",
    "backend/models/schemas",
    "backend/services",
    "backend/utils",
    "backend/tests/unit",
    "backend/tests/integration",
    "backend/database"
)

foreach ($dir in $backendDirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "Created directory: $dir" -ForegroundColor Green
    }
}

# Create backend .env file if it doesn't exist
$envFile = "backend/.env"
if (-not (Test-Path $envFile)) {
    Write-Host "Creating backend .env file..." -ForegroundColor Blue
    @"
DATABASE_URL=sqlite:///./database/restaurant.db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALLOWED_ORIGINS=http://localhost:5173
"@ | Out-File -FilePath $envFile -Encoding utf8
    Write-Host "Created .env file with default values" -ForegroundColor Green
}

# Set up frontend
Write-Host "Setting up frontend..." -ForegroundColor Blue
Set-Location frontend

# Create frontend with Vite if it doesn't exist
if (-not (Test-Path "package.json")) {
    Write-Host "Creating new Vite project..." -ForegroundColor Blue
    npm create vite@latest . -- --template react-ts --skip-git
}

# Create frontend directory structure
Write-Host "Creating frontend directory structure..." -ForegroundColor Blue
$frontendDirs = @(
    "src/assets/icons",
    "src/assets/images",
    "src/components/common",
    "src/components/layout",
    "src/components/menu",
    "src/hooks",
    "src/utils",
    "src/styles",
    "src/services",
    "src/types",
    "src/pages",
    "src/contexts"
)

foreach ($dir in $frontendDirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "Created directory: $dir" -ForegroundColor Green
    }
}

# Create index files for exports
Write-Host "Creating index files for exports..." -ForegroundColor Blue
$indexFiles = @(
    "src/components/common/index.ts",
    "src/components/layout/index.ts",
    "src/components/menu/index.ts",
    "src/hooks/index.ts",
    "src/utils/index.ts",
    "src/services/index.ts",
    "src/types/index.ts",
    "src/contexts/index.ts"
)

foreach ($file in $indexFiles) {
    if (-not (Test-Path $file)) {
        @"
// Export all components/functions from this directory
"@ | Out-File -FilePath $file -Encoding utf8
        Write-Host "Created index file: $file" -ForegroundColor Green
    }
}

# Create Tailwind config
Write-Host "Creating Tailwind configuration..." -ForegroundColor Blue
if (-not (Test-Path "tailwind.config.js")) {
    @"
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: 'rgb(var(--color-primary) / <alpha-value>)',
        secondary: 'rgb(var(--color-secondary) / <alpha-value>)',
        accent: 'rgb(var(--color-accent) / <alpha-value>)',
        background: 'rgb(var(--color-background) / <alpha-value>)',
        surface: 'rgb(var(--color-surface) / <alpha-value>)',
        text: 'rgb(var(--color-text) / <alpha-value>)',
        'text-light': 'rgb(var(--color-text-light) / <alpha-value>)',
      },
      spacing: {
        'header': 'var(--header-height)',
        'footer': 'var(--footer-height)',
        'sidebar': 'var(--sidebar-width)',
      },
      transitionDuration: {
        DEFAULT: 'var(--transition-speed)',
      },
    },
  },
  plugins: [],
  darkMode: 'class',
}
"@ | Out-File -FilePath "tailwind.config.js" -Encoding utf8
    Write-Host "Created Tailwind config" -ForegroundColor Green
}

# Create PostCSS config
Write-Host "Creating PostCSS configuration..." -ForegroundColor Blue
if (-not (Test-Path "postcss.config.js")) {
    @"
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
"@ | Out-File -FilePath "postcss.config.js" -Encoding utf8
    Write-Host "Created PostCSS config" -ForegroundColor Green
}

# Create TypeScript config
Write-Host "Creating TypeScript configuration..." -ForegroundColor Blue
if (-not (Test-Path "tsconfig.json")) {
    @"
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"],
      "@components/*": ["src/components/*"],
      "@hooks/*": ["src/hooks/*"],
      "@utils/*": ["src/utils/*"],
      "@services/*": ["src/services/*"],
      "@types/*": ["src/types/*"],
      "@contexts/*": ["src/contexts/*"],
      "@assets/*": ["src/assets/*"],
      "@styles/*": ["src/styles/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
"@ | Out-File -FilePath "tsconfig.json" -Encoding utf8
    Write-Host "Created TypeScript config" -ForegroundColor Green
}

# Install frontend dependencies
Write-Host "Installing frontend dependencies..." -ForegroundColor Blue
npm install

# Install additional frontend dependencies
Write-Host "Installing additional frontend dependencies..." -ForegroundColor Blue
npm install @headlessui/react @heroicons/react react-router-dom @tanstack/react-query axios

# Install frontend dev dependencies
Write-Host "Installing frontend dev dependencies..." -ForegroundColor Blue
npm install -D tailwindcss postcss autoprefixer @types/node

# Create frontend .env file if it doesn't exist
$frontendEnvFile = ".env"
if (-not (Test-Path $frontendEnvFile)) {
    Write-Host "Creating frontend .env file..." -ForegroundColor Blue
    @"
VITE_API_URL=http://localhost:8000
"@ | Out-File -FilePath $frontendEnvFile -Encoding utf8
    Write-Host "Created frontend .env file with default values" -ForegroundColor Green
}

# Return to root directory
Set-Location ..

Write-Host "`nSetup completed successfully!" -ForegroundColor Green
Write-Host "`nTo start the application:"
Write-Host "1. Start the backend server: python -m uvicorn backend.api.app:app --reload"
Write-Host "2. In another terminal, start the frontend: cd frontend && npm run dev"
Write-Host "`nTo run tests:"
Write-Host "pytest backend/tests/" 