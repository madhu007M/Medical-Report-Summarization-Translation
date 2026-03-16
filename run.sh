#!/bin/bash
# run.sh — Start backend and frontend in parallel (Linux/macOS)
# Usage: ./run.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtual environment if it exists
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

echo "========================================"
echo "  AI Medical Report Interpreter"
echo "  Starting Platform"
echo "========================================"
echo ""
echo "  Backend:  http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo "  Frontend: http://localhost:8501"
echo ""
echo "  Press Ctrl+C to stop all servers"
echo "========================================"
echo ""

# Start backend in background
echo "[1/2] Starting backend server..."
python -m uvicorn backend.app.main:app --reload --port 8000 &
BACKEND_PID=$!

# Wait for backend to initialize
sleep 3

# Start frontend in foreground
echo "[2/2] Starting frontend..."
python -m streamlit run frontend/streamlit_app.py &
FRONTEND_PID=$!

# Wait for both processes; shut down both on Ctrl+C
trap "echo ''; echo 'Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT TERM

wait $BACKEND_PID $FRONTEND_PID
