# Quick Reference Guide

## Final Outcome (At a Glance)

The platform now works as an AI-powered Medical Report Interpreter and Communication Assistant that simplifies clinical reports, translates them into regional languages, provides voice explanations, asks symptom-based follow-up questions, sends SMS/WhatsApp alerts, analyzes location-based health trends, and returns risk severity with actionable guidance.

## Requirement Checklist

| Requirement | Status |
|-------------|--------|
| Simplified AI explanation of report | Achieved |
| Multi-language output | Achieved |
| Voice-based explanation | Achieved |
| Interactive symptom follow-up | Achieved |
| SMS/WhatsApp integration | Achieved |
| Location-based trend analysis | Achieved |
| Conversational symptom chatbot | Achieved |
| Medication-use guidance | Achieved |
| Future health-risk signaling | Achieved |
| Risk and urgency scoring with recommendations | Achieved |

## 🚀 Fast Setup

### Windows
```bash
setup_windows.bat
# Follow prompts
```

### Linux/macOS
```bash
chmod +x setup_linux.sh
./setup_linux.sh
```

## 🧪 Testing

```bash
# All tests
pytest tests/ -v

# Specific module
pytest tests/test_risk_engine.py -v

# With coverage
pytest tests/ --cov=backend --cov-report=html
```

## ▶️ Running

**Terminal 1 - Backend:**
```bash
uvicorn backend.app.main:app --reload --port 8000
# API docs: http://localhost:8000/docs
```

**Terminal 2 - Frontend:**
```bash
streamlit run frontend/streamlit_app.py
# Opens: http://localhost:8501
```

## 🔧 Configuration (`.env`)

```env
# Tesseract (Windows only)
TESSERACT_CMD_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe

# Database
DATABASE_URL=sqlite:///./health_platform.db

# Twilio (optional but recommended)
TWILIO_ACCOUNT_SID=ACxxxx
TWILIO_AUTH_TOKEN=xxxx
TWILIO_FROM_NUMBER=+1234567890

# Models
SUMMARIZER_MODEL=facebook/bart-large-cnn
```

## 📊 New Audio Streaming

Instead of saving to disk, audio now streams via HTTP:

```
GET /audio/explanation?text=Fever&language=en
→ Returns MP3 stream
```

Frontend automatically uses this endpoint.

## 🧬 Test Coverage

| Module | Tests | Focus |
|--------|-------|-------|
| OCR | 7 | Tesseract, PDF, images, fallbacks |
| Summarizer | 4 | Model loading, fallbacks |
| Translation | 6 | All languages, error handling |
| Risk Engine | 10 | Scoring logic, edge cases |
| TTS | 7 | Audio bytes vs files, errors |
| API | 13 | Full endpoint integration |

## 🩹 Troubleshooting

| Issue | Solution |
|-------|----------|
| Tesseract not found | Set `TESSERACT_CMD_PATH` in `.env` |
| Port already in use | Use `--port 8001` instead |
| Models downloading slowly | Models cache locally; just first time |
| SMS not sending | Add valid Twilio credentials to `.env` |
| Tests fail with imports | Run: `pip install -r requirements.txt` |

## 📚 Full Documentation

- Setup & Configuration: [`SETUP_AND_TESTING.md`](SETUP_AND_TESTING.md)
- Architecture & Features: [`README.md`](README.md)
- API Documentation: Run backend, visit `/docs`

## 🎯 Key Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/process-report` | POST | Upload medical report |
| `/audio/explanation` | GET | **Stream audio (NEW)** |
| `/chatbot` | POST | Symptom chatbot |
| `/outbreaks` | GET | Outbreak clusters |
| `/doctor/alerts` | GET/POST | Doctor alerts |

## 💾 Database

Default: SQLite (`health_platform.db`)

For production, use PostgreSQL:
```env
DATABASE_URL=postgresql://user:pass@localhost/medicaldb
```

## 🐳 Docker (Optional)

```bash
docker build -t medical-platform .
docker run -p 8000:8000 medical-platform
```
