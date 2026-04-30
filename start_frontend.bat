@echo off
echo ========================================
echo   AI Medical Report Interpreter
echo   Starting Frontend (Streamlit)
echo ========================================
echo.

cd /d "%~dp0"

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo Starting Streamlit frontend on http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

streamlit run frontend/streamlit_app.py
