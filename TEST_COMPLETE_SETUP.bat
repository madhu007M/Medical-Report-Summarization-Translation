@echo off
echo ========================================
echo   AI Medical Report Interpreter
echo   Complete Setup Verification
echo ========================================
echo.

cd /d "%~dp0"

REM Check Python
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python.
    pause
    exit /b 1
)
echo ✓ Python found

REM Check Node.js
echo Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found. Please install Node.js.
    pause
    exit /b 1
)
echo ✓ Node.js found

REM Check venv
echo Checking Python virtual environment...
if not exist ".venv\Scripts\activate.bat" (
    echo ERROR: Python virtual environment not found.
    echo Run: python -m venv .venv
    pause
    exit /b 1
)
echo ✓ Virtual environment found

REM Check frontend dependencies
echo Checking frontend dependencies...
if not exist "frontend-vite\node_modules" (
    echo ERROR: Frontend dependencies not installed.
    echo Run: cd frontend-vite && npm install
    pause
    exit /b 1
)
echo ✓ Frontend dependencies found

REM Check backend imports
echo Checking backend application...
call .venv\Scripts\activate.bat
python -c "import backend.app.main; print('OK')" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Backend application import failed.
    pause
    exit /b 1
)
echo ✓ Backend application verified

echo.
echo ========================================
echo   All checks passed!
echo ========================================
echo.
echo You can now start the platform with:
echo   - START_PLATFORM.bat (both services)
echo   - start_backend.bat (backend only)
echo   - start_frontend.bat (frontend only)
echo.
echo Backend API: http://localhost:8000
echo Frontend: http://localhost:5173
echo.
pause
