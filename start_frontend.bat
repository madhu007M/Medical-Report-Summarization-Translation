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
echo Starting frontend server...
echo The app will open in your browser automatically
echo URL: http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

python -m streamlit run frontend/streamlit_app.py
