#!/bin/bash
# Setup script for RFID Attendance System

set -e

echo "=========================================="
echo "RFID Attendance System - Setup Script"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version || { echo "Python 3 is required but not installed. Aborting."; exit 1; }

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
echo ""
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    
    # Generate a random secret key
    echo "Generating secret key..."
    SECRET_KEY=$(python3 -c 'import os; import base64; print(base64.b64encode(os.urandom(32)).decode())')
    
    # Update .env with generated key
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/CHANGE-THIS-TO-A-RANDOM-SECRET-KEY/$SECRET_KEY/" .env
    else
        sed -i "s/CHANGE-THIS-TO-A-RANDOM-SECRET-KEY/$SECRET_KEY/" .env
    fi
    
    echo "✓ .env file created with random secret key"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env file and configure:"
    echo "   - DATABASE_URL (your database connection)"
    echo "   - MQTT_BROKER (your MQTT broker address)"
    echo "   - Email settings (if needed)"
else
    echo "✓ .env file already exists"
fi

# Create uploads directory
echo ""
echo "Creating uploads directory..."
mkdir -p uploads
echo "✓ Uploads directory created"

# Database setup prompt
echo ""
echo "=========================================="
echo "Database Setup"
echo "=========================================="
echo ""
echo "Do you want to set up PostgreSQL database? (y/n)"
read -r setup_db

if [ "$setup_db" = "y" ] || [ "$setup_db" = "Y" ]; then
    echo ""
    echo "Setting up PostgreSQL..."
    echo "Please run the following commands in PostgreSQL:"
    echo ""
    echo "  CREATE DATABASE karty;"
    echo "  CREATE USER karty WITH PASSWORD 'karty';"
    echo "  GRANT ALL PRIVILEGES ON DATABASE karty TO karty;"
    echo ""
    echo "Press Enter when done..."
    read -r
    
    echo ""
    echo "Running database migrations..."
    alembic upgrade head || echo "⚠️  Alembic migrations not yet configured"
fi

# Summary
echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Review and update .env file with your settings"
echo ""
echo "2. Start the API server:"
echo "   source venv/bin/activate"
echo "   uvicorn main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "3. In another terminal, start the MQTT listener:"
echo "   source venv/bin/activate"
echo "   python3 -m src.mqtt_handler"
echo ""
echo "4. Access the API:"
echo "   - API: http://localhost:8000"
echo "   - Docs: http://localhost:8000/docs"
echo ""
echo "For more information, see:"
echo "   - README-new.md"
echo "   - MIGRATION.md"
echo ""
echo "=========================================="
