@echo off
echo ========================================
echo   AI Medical Report Interpreter
echo   Starting Frontend (Vite + React)
echo ========================================
echo.

cd /d "%~dp0\frontend-vite"

echo.
echo Starting frontend server on http://localhost:5173
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

call npm run dev

streamlit run frontend/streamlit_app.py
