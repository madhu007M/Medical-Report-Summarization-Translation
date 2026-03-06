"""
FastAPI main application for the AI Medical Report Interpreter Platform.

Architecture:
  Report Upload → Text Extraction → Medical Summarization → Risk Detection
  → Translation → Voice Generation → Chatbot Interaction
  → Messaging & Community Alerts
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.config import AUDIO_DIR, UPLOAD_DIR
from backend.models.database import init_db
from backend.api import reports, translation, chatbot, risk, messaging, alerts, doctor

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Application lifecycle
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up — initialising database …")
    init_db()
    logger.info("Database ready.")
    yield
    logger.info("Shutting down.")


# ---------------------------------------------------------------------------
# FastAPI instance
# ---------------------------------------------------------------------------

app = FastAPI(
    title="AI Medical Report Interpreter & Community Health Platform",
    description=(
        "Upload medical reports (PDF/image/text), get plain-language summaries, "
        "multilingual translation, voice explanations, risk scoring, symptom chatbot, "
        "WhatsApp/SMS notifications, and community outbreak alerts."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow Streamlit frontend and local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve generated audio files as static assets
app.mount("/audio", StaticFiles(directory=str(AUDIO_DIR)), name="audio")

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(reports.router)
app.include_router(translation.router)
app.include_router(chatbot.router)
app.include_router(risk.router)
app.include_router(messaging.router)
app.include_router(alerts.router)
app.include_router(doctor.router)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "AI Medical Report Interpreter Platform"}


@app.get("/", tags=["Health"])
def root():
    return {
        "message": "Welcome to the AI Medical Report Interpreter & Community Health Platform",
        "docs": "/docs",
        "redoc": "/redoc",
    }
