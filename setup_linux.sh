#!/bin/bash

# Setup script for Medical Platform on Linux/macOS

echo "========================================"
echo "Medical Platform Setup Script"
echo "========================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found. Please install Python 3.10+"
    exit 1
fi

echo "[1/6] Creating virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

echo "[2/6] Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "[3/6] Installing system dependencies..."
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Detected Linux. Installing Tesseract..."
    sudo apt-get update
    sudo apt-get install -y tesseract-ocr
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Detected macOS. Installing Tesseract..."
    if ! command -v brew &> /dev/null; then
        echo "ERROR: Homebrew not found. Please install Homebrew first"
        exit 1
    fi
    brew install tesseract
fi

echo "[4/6] Verifying Tesseract installation..."
if command -v tesseract &> /dev/null; then
    echo "OK: Tesseract found"
    tesseract --version | head -1
else
    echo "WARNING: Tesseract not found. Installation may have failed."
fi

echo "[5/6] Creating .env file if not exists..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file - please update with your credentials"
else
    echo "OK: .env file exists"
fi

echo "[6/6] Database initialization..."
python3 -c "from backend.app.db import Base, engine; Base.metadata.create_all(bind=engine); print('Database ready')"

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your Twilio credentials (optional)"
echo "2. Terminal 1: python3 -m uvicorn backend.app.main:app --reload --port 8000"
echo "3. Terminal 2: python3 -m streamlit run frontend/streamlit_app.py"
echo ""
echo "Run tests: pytest tests/ -v"
echo ""
