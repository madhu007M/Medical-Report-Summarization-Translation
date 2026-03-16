# AI Medical Report Interpreter & Community Health Platform

Prototype that converts medical reports into patient-friendly explanations, scores risk, translates into multiple languages, produces voice guidance, supports SMS/WhatsApp alerts, and detects location-based symptom clusters.

## Project Outcome

This project delivers an AI-powered Medical Report Interpreter and Communication Assistant designed to help patients understand complex medical reports regardless of literacy level or language background. The platform analyzes uploaded reports using AI, produces simplified patient-friendly explanations, and translates the results into multiple regional languages to improve comprehension of health conditions.

To improve accessibility, it includes a voice-based explanation flow for users who are unable to read. The system also supports interactive symptom-based follow-up questioning, where AI asks context-aware questions derived from report findings (for example, fever- or chest-pain-related prompts) to improve clarity and triage accuracy.

In addition, the platform integrates SMS/WhatsApp communication so patients can receive summaries, alerts, and guidance on their phones, including in low-connectivity settings. With optional location data, the system analyzes regional symptom patterns to detect potential outbreak clusters and estimate local disease criticality.

A conversational chatbot further supports patients by analyzing symptoms, providing safe medication-use guidance, and highlighting possible near-term risk progression signals. To strengthen decision support, the platform includes medical risk detection and urgency scoring that classifies cases into severity levels and provides actionable recommendations, such as immediate emergency care or routine consultation.

Overall, the platform acts as an AI-driven healthcare interpreter and guidance system that bridges the gap between complex clinical information and patient understanding, with strong value for rural and low-literacy populations.

## Capability Checklist

| Requirement | Status | Implementation |
|-------------|--------|----------------|
| AI simplification of medical reports | Achieved | OCR + summarizer pipeline (`/process-report`) |
| Multilingual translation | Achieved | On-pipeline and on-demand translation (`/translate`) with fallback |
| Voice explanation for low-literacy users | Achieved | Streaming TTS endpoint (`/audio/explanation`) |
| Interactive symptom follow-up questions | Achieved | Report-driven question generation in `follow_up` payload |
| SMS/WhatsApp communication | Achieved | Twilio messaging service with simulation mode for testing |
| Location-aware trend and criticality analysis | Achieved | Symptom cluster/outbreak detection (`/outbreaks`) |
| Conversational health chatbot | Achieved | Context-aware chatbot endpoint (`/chatbot`) |
| Medication guidance support | Achieved | Chatbot insights detect medicine keywords and provide safe-use tips |
| Future-risk indication | Achieved | Chatbot insights generate near-term risk signals |
| Risk detection and urgency scoring | Achieved | Risk engine returns severity, alerts, and recommendations |

## Architecture

Pipeline: Report Upload → OCR Text Extraction → Medical NLP Summarization → Risk Detection & Urgency Scoring → Multilingual Translation → Voice Explanation → Symptom Chatbot Interaction → Messaging Alerts → Location-Based Outbreak Detection → Doctor Alert Dashboard.

Components:
- FastAPI backend (`backend/app`) with OCR, summarizer, translation, risk engine, chatbot, messaging, outbreak detection, and doctor alerts.
- Streamlit frontend (`frontend/streamlit_app.py`) for uploads, summaries, voice playback, chatbot, and viewing doctor alerts.
- SQLite (default) via SQLAlchemy; configurable via `DATABASE_URL`.
- Hugging Face transformers: summarization (default `facebook/bart-large-cnn`) and Marian MT translators for Hindi, Kannada, Tamil.
- OCR: PyPDF2 for PDFs, Pillow + PyTesseract for images; plaintext passthrough for `.txt`.
- **TTS: gTTS with HTTP streaming** (new `/audio/explanation` endpoint) instead of filesystem files.
- Messaging: Twilio SMS/WhatsApp (if credentials provided).

## Quick Start

### Automated Setup

**Windows:**
```bash
setup_windows.bat
```

**Linux/macOS:**
```bash
chmod +x setup_linux.sh
./setup_linux.sh
```

### Manual Setup

1) Python environment
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
```

2) System dependencies
- **Windows**: Install [Tesseract OCR](https://github.com/tesseract-ocr/tesseract/wiki/Downloads), then set `TESSERACT_CMD_PATH` in `.env`
- **Linux**: `sudo apt-get install tesseract-ocr`
- **macOS**: `brew install tesseract`

3) Configuration
```bash
cp .env.example .env
# Edit .env with your credentials (see SETUP_AND_TESTING.md for details)
```

## Running

### One Command (Linux/macOS)
```bash
chmod +x run.sh
./run.sh
```

### Backend (FastAPI + Uvicorn)
```bash
python -m uvicorn backend.app.main:app --reload --port 8000
```
- Interactive API docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Frontend (Streamlit)
```bash
python -m streamlit run frontend/streamlit_app.py
```
- Opens at: `http://localhost:8501`

## Testing

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Test Suites
```bash
pytest tests/test_ocr_module.py -v              # OCR extraction & Tesseract
pytest tests/test_summarizer_module.py -v       # Summarization with fallbacks
pytest tests/test_translation_module.py -v      # Multilingual translation
pytest tests/test_risk_engine.py -v             # Risk scoring
pytest tests/test_tts_module.py -v              # Audio generation & streaming
pytest tests/test_api_endpoints.py -v           # API contract tests
```

### Coverage Report
```bash
pytest tests/ --cov=backend --cov-report=html
# Open htmlcov/index.html in browser
```

## Key Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/health` | Service status |
| POST | `/process-report` | Upload and process medical report |
| POST | `/chatbot` | Symptom follow-up chatbot |
| GET | `/outbreaks` | Detect outbreak clusters |
| GET/POST | `/doctor/alerts` | Doctor regional health alerts |
| **GET** | **`/audio/explanation`** | **Stream audio explanation (NEW)** |

## Features

### 1. Report Processing
- Upload: PDF, image (JPG/PNG), or plaintext
- OCR: Tesseract (images) or PyPDF2 (PDFs)
- Summarization: BART converts medical jargon to simple language
- Risk Scoring: Low/Moderate/High with recommendations

### 2. Multilingual Support
- Translates to: English, Hindi, Kannada, Tamil
- Graceful fallback on errors

### 3. Voice Explanations (NEW)
- Stream audio via HTTP: `/audio/explanation?text={text}&language={language}`
- No disk files needed; works over network
- Supports 100+ languages via gTTS

### 4. Symptom Chatbot
- Follow-up questions based on symptoms
- Rule-based medical guidance
- Session persistence

### 5. Messaging Alerts
- SMS/WhatsApp via Twilio (optional)
- Automatic notifications

### 6. Outbreak Detection
- Location-based symptom clustering
- Detects potential disease outbreaks

### 7. Doctor Dashboard
- Regional health alerts
- Disease awareness broadcasting

## Configuration

See `.env.example` for all options. Key variables:
```
TESSERACT_CMD_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe  # Windows only
DATABASE_URL=sqlite:///./health_platform.db
SUMMARIZER_MODEL=facebook/bart-large-cnn
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_FROM_NUMBER=+1234567890
```

## Notes
- Models auto-download on first use (~5GB); ensure disk space
- Tesseract required for image OCR; optional for text/PDF
- Twilio credentials optional; messaging skips if absent
- Audio now streams via HTTP (no filesystem needed)

## For Detailed Instructions

See [**SETUP_AND_TESTING.md**](SETUP_AND_TESTING.md) for:
- Step-by-step Tesseract/Twilio setup
- Comprehensive testing workflows  
- Docker deployment
- Production checklist
- Troubleshooting
