# Setup script for RFID Attendance System (Windows PowerShell)
# Run with: powershell -ExecutionPolicy Bypass -File setup.ps1

Write-Host "===========================================" -ForegroundColor Cyan
Write-Host "RFID Attendance System - Setup Script" -ForegroundColor Cyan
Write-Host "Windows PowerShell Version" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "Checking Python version..." -ForegroundColor Yellow
python --version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python is not installed or not in PATH. Aborting." -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host ""
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
if (-Not (Test-Path ".venv")) {
    python -m venv .venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✓ Virtual environment already exists" -ForegroundColor Green
}

# Activate virtual environment
Write-Host ""
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\.venv\Scripts\Activate.ps1"
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "ERROR: Could not activate virtual environment" -ForegroundColor Red
    exit 1
}

# Upgrade pip
Write-Host ""
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
Write-Host "✓ pip upgraded" -ForegroundColor Green

# Install requirements
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Create .env file if it doesn't exist
Write-Host ""
if (-Not (Test-Path ".env")) {
    Write-Host "Creating .env file..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env" -ErrorAction SilentlyContinue
    
    # Generate a random secret key
    Write-Host "Generating secret key..." -ForegroundColor Yellow
    $secretKey = python -c "import os; import base64; print(base64.b64encode(os.urandom(32)).decode())"
    
    # Update .env with generated key
    (Get-Content ".env") -replace "CHANGE-THIS-TO-A-RANDOM-SECRET-KEY", $secretKey | Set-Content ".env"
    
    Write-Host "✓ .env file created with random secret key" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠️  IMPORTANT: Please edit .env file and configure:" -ForegroundColor Yellow
    Write-Host "   - DATABASE_URL (your database connection)" -ForegroundColor Yellow
    Write-Host "   - MQTT_BROKER (your MQTT broker address)" -ForegroundColor Yellow
    Write-Host "   - Email settings (if needed)" -ForegroundColor Yellow
} else {
    Write-Host "✓ .env file already exists" -ForegroundColor Green
}

# Create uploads directory
Write-Host ""
Write-Host "Creating uploads directory..." -ForegroundColor Yellow
if (-Not (Test-Path "uploads")) {
    New-Item -ItemType Directory -Path "uploads" -Force | Out-Null
}
Write-Host "✓ Uploads directory created/verified" -ForegroundColor Green

# Database setup prompt
Write-Host ""
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host "Database Setup" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "SQLite database will be created automatically at ./karty.db" -ForegroundColor Cyan
Write-Host ""
Write-Host "For PostgreSQL setup, please create database manually:" -ForegroundColor Yellow
Write-Host "  psql -U postgres" -ForegroundColor Gray
Write-Host "  CREATE DATABASE karty;" -ForegroundColor Gray
Write-Host "  CREATE USER karty WITH PASSWORD 'karty';" -ForegroundColor Gray
Write-Host "  GRANT ALL PRIVILEGES ON DATABASE karty TO karty;" -ForegroundColor Gray
Write-Host ""
Write-Host "Then update DATABASE_URL in .env to:" -ForegroundColor Yellow
Write-Host "  DATABASE_URL=postgresql://karty:karty@localhost/karty" -ForegroundColor Gray
Write-Host ""

$setupDb = Read-Host "Run Alembic migrations now? (y/n)"

if ($setupDb -eq "y" -or $setupDb -eq "Y") {
    Write-Host ""
    Write-Host "Running database migrations..." -ForegroundColor Yellow
    alembic upgrade head
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Migrations completed" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Migrations failed or Alembic not configured" -ForegroundColor Yellow
    }
}

# Summary
Write-Host ""
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Review and update .env file with your settings" -ForegroundColor White
Write-Host ""
Write-Host "2. Start the API server:" -ForegroundColor White
Write-Host "   .venv\Scripts\activate" -ForegroundColor Gray
Write-Host "   uvicorn main:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor Gray
Write-Host ""
Write-Host "3. In another terminal, start the MQTT listener:" -ForegroundColor White
Write-Host "   .venv\Scripts\activate" -ForegroundColor Gray
Write-Host "   python -m src.mqtt_handler" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Access the API:" -ForegroundColor White
Write-Host "   - API: http://localhost:8000" -ForegroundColor Gray
Write-Host "   - Docs: http://localhost:8000/docs" -ForegroundColor Gray
Write-Host "   - Health: http://localhost:8000/health" -ForegroundColor Gray
Write-Host ""
Write-Host "For more information, see:" -ForegroundColor White
Write-Host "   - README.md" -ForegroundColor Gray
Write-Host "   - HowToSetup.md" -ForegroundColor Gray
Write-Host "   - MIGRATION.md" -ForegroundColor Gray
Write-Host ""
Write-Host "===========================================" -ForegroundColor Cyan
