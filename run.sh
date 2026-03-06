#!/usr/bin/env bash
# =============================================================================
# run.sh — Start the AI Medical Report Interpreter Platform
#
# Usage:
#   ./run.sh              # start both backend + frontend
#   ./run.sh backend      # start backend only
#   ./run.sh frontend     # start frontend only
#
# Prerequisites:
#   pip install -r requirements-minimal.txt   (quick start, no ML models)
#   pip install -r requirements.txt           (full features with AI models)
# =============================================================================

set -e

BACKEND_PORT=${BACKEND_PORT:-8000}
FRONTEND_PORT=${FRONTEND_PORT:-8501}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Load .env if it exists
if [ -f "$SCRIPT_DIR/.env" ]; then
    set -a
    source "$SCRIPT_DIR/.env"
    set +a
    echo "✅  Loaded environment from .env"
fi

start_backend() {
    echo "🚀  Starting FastAPI backend on port $BACKEND_PORT …"
    cd "$SCRIPT_DIR"
    python -m uvicorn backend.main:app \
        --host 0.0.0.0 \
        --port "$BACKEND_PORT" \
        --reload
}

start_frontend() {
    echo "🖥️   Starting Streamlit frontend on port $FRONTEND_PORT …"
    cd "$SCRIPT_DIR"
    export API_BASE_URL="http://localhost:$BACKEND_PORT"
    python -m streamlit run frontend/app.py \
        --server.port "$FRONTEND_PORT" \
        --server.address 0.0.0.0
}

MODE="${1:-both}"

case "$MODE" in
    backend)
        start_backend
        ;;
    frontend)
        start_frontend
        ;;
    both)
        echo "======================================================="
        echo "  AI Medical Report Interpreter Platform"
        echo "  Backend  → http://localhost:$BACKEND_PORT"
        echo "  API Docs → http://localhost:$BACKEND_PORT/docs"
        echo "  Frontend → http://localhost:$FRONTEND_PORT"
        echo "======================================================="
        # Start backend in background, then start frontend in foreground
        start_backend &
        BACKEND_PID=$!
        echo "   Backend PID: $BACKEND_PID"
        sleep 2
        start_frontend
        wait $BACKEND_PID
        ;;
    *)
        echo "Usage: $0 [backend|frontend|both]"
        exit 1
        ;;
esac
