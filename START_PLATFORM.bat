@echo off
echo ========================================
echo   AI Medical Report Interpreter
echo   Starting Complete Platform
echo ========================================
echo.
echo This will start both backend and frontend servers
echo in separate windows.
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:8501
echo.
echo Press any key to continue...
pause >nul

cd /d "%~dp0"

echo.
echo [1/2] Starting Backend Server...
start "Medical Platform - Backend" cmd /k start_backend.bat

echo Waiting 5 seconds for backend to initialize...
timeout /t 5 /nobreak >nul

echo.
echo [2/2] Starting Frontend...
start "Medical Platform - Frontend" cmd /k start_frontend.bat

echo.
echo ========================================
echo   Platform Started Successfully!
echo ========================================
echo.
echo Two new windows have opened:
echo   1. Backend Server  (http://localhost:8000)
echo   2. Frontend UI     (http://localhost:8501)
echo.
echo The Streamlit app should open in your browser automatically.
echo If not, manually visit: http://localhost:8501
echo.
echo To stop the servers, close both terminal windows
echo or press Ctrl+C in each window.
echo.
echo ========================================
echo.
pause
