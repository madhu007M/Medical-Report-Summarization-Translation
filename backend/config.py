"""
Configuration settings for the Medical Report Platform.
All secrets should be provided via environment variables.
"""

import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
AUDIO_DIR = BASE_DIR / "audio_output"

# Ensure directories exist
UPLOAD_DIR.mkdir(exist_ok=True)
AUDIO_DIR.mkdir(exist_ok=True)

# Database
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/medical_platform.db")

# AI Models
SUMMARIZATION_MODEL = os.getenv("SUMMARIZATION_MODEL", "facebook/bart-large-cnn")
TRANSLATION_MODEL_PREFIX = os.getenv("TRANSLATION_MODEL_PREFIX", "Helsinki-NLP/opus-mt")

# Twilio
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")

# Secret key for JWT authentication
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Supported languages for translation
SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "kn": "Kannada",
    "ta": "Tamil",
}

# Risk thresholds for common blood test values
RISK_THRESHOLDS = {
    "glucose": {"low": 70, "high_moderate": 140, "high_severe": 200, "unit": "mg/dL"},
    "hemoglobin": {"low_severe": 7, "low_moderate": 10, "normal_min": 12, "unit": "g/dL"},
    "wbc": {"low": 4.0, "high_moderate": 11.0, "high_severe": 15.0, "unit": "K/uL"},
    "creatinine": {"high_moderate": 1.2, "high_severe": 2.0, "unit": "mg/dL"},
    "bp_systolic": {"low": 90, "high_moderate": 140, "high_severe": 180, "unit": "mmHg"},
    "bp_diastolic": {"low": 60, "high_moderate": 90, "high_severe": 120, "unit": "mmHg"},
    "temperature": {"low": 96.0, "high_moderate": 100.4, "high_severe": 103.0, "unit": "°F"},
    "spo2": {"low_severe": 90, "low_moderate": 94, "normal_min": 95, "unit": "%"},
}
