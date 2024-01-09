# Validation script for Restaurant Application

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

# Function to test HTTP endpoint
function Test-HttpEndpoint {
    param(
        [string]$Uri,
        [string]$Method = "GET",
        [int]$TimeoutSec = 5
    )
    try {
        $response = Invoke-WebRequest -Uri $Uri -Method $Method -TimeoutSec $TimeoutSec -ErrorAction Stop
        return $response.StatusCode -eq 200
    } catch {
        return $false
    }
}

# Initialize validation status
$validationErrors = @()
$validationWarnings = @()

Write-Host "Starting validation..." -ForegroundColor Blue

# Check Python environment
Write-Host "`nChecking Python environment..." -ForegroundColor Blue
if (-not (Test-Command python)) {
    $validationErrors += "Python is not installed"
} else {
    $pythonVersion = python --version
    Write-Host "Found $pythonVersion" -ForegroundColor Green
}

# Check virtual environment
Write-Host "`nChecking virtual environment..." -ForegroundColor Blue
if (-not (Test-Path "venv")) {
    $validationErrors += "Virtual environment not found"
} else {
    Write-Host "Virtual environment exists" -ForegroundColor Green
}

# Check Node.js
Write-Host "`nChecking Node.js..." -ForegroundColor Blue
if (-not (Test-Command node)) {
    $validationErrors += "Node.js is not installed"
} else {
    $nodeVersion = node --version
    Write-Host "Found Node.js $nodeVersion" -ForegroundColor Green
}

# Check project structure
Write-Host "`nChecking project structure..." -ForegroundColor Blue
$requiredDirs = @(
    "backend/api",
    "backend/models",
    "backend/services",
    "backend/utils",
    "backend/tests",
    "frontend"
)

foreach ($dir in $requiredDirs) {
    if (-not (Test-Path $dir)) {
        $validationErrors += "Missing directory: $dir"
    } else {
        Write-Host "Found directory: $dir" -ForegroundColor Green
    }
}

# Check configuration files
Write-Host "`nChecking configuration files..." -ForegroundColor Blue
$requiredFiles = @(
    "pyproject.toml",
    "setup.py",
    "backend/.env",
    "frontend/.env"
)

foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        $validationErrors += "Missing file: $file"
    } else {
        Write-Host "Found file: $file" -ForegroundColor Green
    }
}

# Check backend dependencies
Write-Host "`nChecking backend dependencies..." -ForegroundColor Blue
try {
    python -c "import fastapi, uvicorn, sqlalchemy, pydantic" 2>$null
    Write-Host "All required Python packages are installed" -ForegroundColor Green
} catch {
    $validationErrors += "Missing required Python packages"
}

# Check frontend dependencies
Write-Host "`nChecking frontend dependencies..." -ForegroundColor Blue
Set-Location frontend
if (Test-Path "node_modules") {
    Write-Host "Frontend dependencies are installed" -ForegroundColor Green
} else {
    $validationErrors += "Frontend dependencies are not installed"
}
Set-Location ..

# Check if services are running
Write-Host "`nChecking services..." -ForegroundColor Blue

# Check backend API
$backendUrl = "http://localhost:8000/health"
if (Test-HttpEndpoint -Uri $backendUrl) {
    Write-Host "Backend API is running" -ForegroundColor Green
} else {
    $validationWarnings += "Backend API is not running"
}

# Check frontend dev server
$frontendUrl = "http://localhost:5173"
if (Test-HttpEndpoint -Uri $frontendUrl) {
    Write-Host "Frontend dev server is running" -ForegroundColor Green
} else {
    $validationWarnings += "Frontend dev server is not running"
}

# Summary
Write-Host "`nValidation Summary:" -ForegroundColor Blue
if ($validationErrors.Count -eq 0 -and $validationWarnings.Count -eq 0) {
    Write-Host "All checks passed successfully!" -ForegroundColor Green
} else {
    if ($validationErrors.Count -gt 0) {
        Write-Host "`nErrors:" -ForegroundColor Red
        $validationErrors | ForEach-Object { Write-Host "- $_" -ForegroundColor Red }
    }
    if ($validationWarnings.Count -gt 0) {
        Write-Host "`nWarnings:" -ForegroundColor Yellow
        $validationWarnings | ForEach-Object { Write-Host "- $_" -ForegroundColor Yellow }
    }
}

# Provide next steps
Write-Host "`nNext Steps:" -ForegroundColor Blue
if ($validationWarnings -contains "Backend API is not running") {
    Write-Host "- Start the backend: uvicorn backend.api.app:app --reload"
}
if ($validationWarnings -contains "Frontend dev server is not running") {
    Write-Host "- Start the frontend: cd frontend && npm run dev"
}
if ($validationErrors.Count -gt 0) {
    Write-Host "- Run setup.ps1 to fix missing components"
} 