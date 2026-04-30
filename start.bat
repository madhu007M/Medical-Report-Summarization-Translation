@echo off
echo ========================================
echo MediAI Frontend - Quick Start
echo ========================================
echo.

echo [1/3] Installing dependencies...
call npm install
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [2/3] Dependencies installed successfully!
echo.

echo [3/3] Starting development server...
echo.
echo Backend should be running at: http://localhost:8000
echo Frontend will start at: http://localhost:5173
echo.
echo Press Ctrl+C to stop the server
echo.

call npm run dev
