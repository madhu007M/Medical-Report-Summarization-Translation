@echo off
REM Setup script for Medical Platform on Windows

echo ========================================
echo Medical Platform Setup Script (Windows)
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Please install Python 3.10+
    pause
    exit /b 1
)

echo [1/5] Creating virtual environment...
python -m venv .venv
call .venv\Scripts\activate.bat

echo [2/5] Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

echo [3/5] Checking Tesseract installation...
where tesseract >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Tesseract not found in PATH
    echo Install from: https://github.com/tesseract-ocr/tesseract/wiki/Downloads
    echo Then update TESSERACT_CMD_PATH in .env file
) else (
    echo OK: Tesseract found in PATH
)

echo [4/5] Creating .env file if not exists...
if not exist .env (
    copy .env.example .env
    echo Created .env file - please update with your credentials
) else (
    echo OK: .env file exists
)

echo [5/5] Database initialization...
python -c "from backend.app.db import Base, engine; Base.metadata.create_all(bind=engine); print('Database ready')"

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Edit .env file with your Twilio credentials (if available)
echo 2. Terminal 1: python -m uvicorn backend.app.main:app --reload --port 8000
echo 3. Terminal 2: python -m streamlit run frontend/streamlit_app.py
echo.
echo Run tests: pytest tests/ -v
echo.
pause
