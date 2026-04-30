#!/usr/bin/env bash
echo "========================================"
echo "  AI Medical Report Interpreter"
echo "  Starting Backend Server (FastAPI)"
echo "========================================"
echo

cd "$(dirname "$0")"

echo "Activating virtual environment..."
source .venv/bin/activate

echo
echo "Starting backend server on http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo
echo "Press Ctrl+C to stop the server"
echo "========================================"
echo

uvicorn backend.app.main:app --reload --port 8000
