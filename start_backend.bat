@echo off
echo ========================================
echo   AI Medical Report Interpreter
echo   Starting Backend Server (FastAPI)
echo ========================================
echo.

cd /d "%~dp0"

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo Starting backend server on http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

uvicorn backend.app.main:app --reload --port 8000
