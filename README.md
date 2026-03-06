# AI Medical Report Interpreter & Community Health Communication Platform

A complete, modular AI-powered prototype that helps patients understand complex medical reports regardless of language or literacy level, while enabling community health monitoring and doctor-driven awareness messaging.

---

## 🏗️ Architecture

```
Report Upload → Text Extraction (OCR) → AI Summarization → Risk Detection
    → Multilingual Translation → Voice Generation → Chatbot Interaction
         → SMS / WhatsApp Messaging → Community Outbreak Alerts
                   → Doctor Dashboard Broadcasts
```

---

## ✨ Features

| Module | Description | Technology |
|--------|-------------|------------|
| **Report Upload** | PDF, image (JPG/PNG/BMP/TIFF), or plain text | FastAPI file upload |
| **OCR Extraction** | Extract text from scanned documents | EasyOCR / Tesseract / pdfplumber |
| **AI Summarization** | Patient-friendly plain-language summary | BART (`facebook/bart-large-cnn`) via HuggingFace |
| **Risk Detection** | Analyse vitals (glucose, BP, Hb, WBC, SpO2) and classify severity | Rule-based thresholds |
| **Multilingual Translation** | English → Hindi / Kannada / Tamil | MarianMT (`Helsinki-NLP`) |
| **Voice Explanation** | Text-to-speech audio for illiterate users | gTTS |
| **Symptom Chatbot** | Follow-up questions based on report content | Rule-based NLP |
| **SMS / WhatsApp** | Send summaries and alerts | Twilio |
| **Outbreak Detection** | Cluster symptoms to detect dengue/flu/COVID outbreaks | Location + symptom analysis |
| **Doctor Dashboard** | Authenticated portal for broadcasting alerts | JWT + FastAPI |
| **Frontend** | Interactive web interface | Streamlit |
| **Database** | Persistent storage | SQLite (default) / PostgreSQL |

---

## 📁 Project Structure

```
├── backend/
│   ├── main.py               # FastAPI application entry point
│   ├── config.py             # Configuration & environment variables
│   ├── api/
│   │   ├── reports.py        # Upload, OCR, summarize, TTS, translate
│   │   ├── translation.py    # On-demand translation endpoint
│   │   ├── chatbot.py        # Symptom chatbot API
│   │   ├── risk.py           # Risk analysis endpoint
│   │   ├── messaging.py      # Twilio SMS / WhatsApp
│   │   ├── alerts.py         # Symptom logging & outbreak alerts
│   │   └── doctor.py         # Doctor dashboard & authentication
│   ├── models/
│   │   └── database.py       # SQLAlchemy ORM models
│   └── services/
│       ├── ocr_service.py    # EasyOCR / Tesseract / pdfplumber
│       ├── summarizer.py     # HuggingFace BART summarization
│       ├── translator.py     # MarianMT / googletrans translation
│       ├── tts_service.py    # gTTS audio generation
│       ├── risk_service.py   # Rule-based risk detection
│       ├── chatbot_service.py# Symptom follow-up chatbot
│       ├── messaging_service.py  # Twilio integration
│       └── location_service.py   # Outbreak detection
├── frontend/
│   └── app.py                # Streamlit web interface
├── tests/
│   └── test_services.py      # Unit tests
├── uploads/                  # Uploaded report files (auto-created)
├── audio_output/             # Generated audio files (auto-created)
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.10+
- (Optional) Tesseract OCR for enhanced image OCR: [Installation guide](https://github.com/tesseract-ocr/tesseract)
- (Optional) Twilio account for SMS/WhatsApp

### 2. Clone & Install

```bash
git clone https://github.com/madhu007M/Medical-Report-Summarization-Translation.git
cd Medical-Report-Summarization-Translation

# Create a virtual environment
python -m venv venv
source venv/bin/activate        # Linux/macOS
# venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your credentials
```

### 4. Start the Backend

```bash
uvicorn backend.main:app --reload --port 8000
```

The interactive API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 5. Start the Frontend

Open a **new terminal**:

```bash
streamlit run frontend/app.py
```

The Streamlit app opens at http://localhost:8501.

---

## 🔧 Environment Variables

Copy `.env.example` to `.env` and fill in the values:

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | No | SQLAlchemy URL (default: SQLite) |
| `SUMMARIZATION_MODEL` | No | HuggingFace model ID (default: `facebook/bart-large-cnn`) |
| `SECRET_KEY` | **Yes (prod)** | JWT signing key |
| `TWILIO_ACCOUNT_SID` | For SMS/WA | Twilio Account SID |
| `TWILIO_AUTH_TOKEN` | For SMS/WA | Twilio Auth Token |
| `TWILIO_PHONE_NUMBER` | For SMS | Twilio phone number |
| `TWILIO_WHATSAPP_NUMBER` | For WhatsApp | Twilio WhatsApp sandbox number |
| `API_BASE_URL` | No | Backend URL seen by Streamlit (default: `http://localhost:8000`) |

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

Tests cover:
- Risk detection logic (glucose, BP, haemoglobin, WBC, SpO2, temperature)
- Chatbot follow-up question flow
- Disease inference from symptom clusters
- OCR plain-text extraction
- Summarizer rule-based fallback
- Messaging graceful failure without credentials

---

## 📡 API Reference

### Report Processing

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/reports/upload` | Upload & process a medical report |
| `GET` | `/reports/{id}` | Get a processed report |
| `GET` | `/reports/{id}/audio/{lang}` | Stream voice audio explanation |
| `GET` | `/reports/` | List all reports |

### Translation

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/translate/` | Translate to a single language |
| `POST` | `/translate/all` | Translate to all languages |
| `GET` | `/translate/languages` | List supported languages |

### Chatbot

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/chatbot/start/{report_id}` | Start a chat session |
| `POST` | `/chatbot/chat` | Send a message |
| `GET` | `/chatbot/session/{id}` | Get session history |

### Risk Analysis

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/risk/analyse` | Analyse text + symptoms for risk |

### Messaging

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/messaging/send-summary` | Send report summary via SMS/WhatsApp |
| `POST` | `/messaging/broadcast` | Broadcast alert to multiple numbers |

### Community Alerts

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/alerts/log-symptoms` | Log symptoms for monitoring |
| `GET` | `/alerts/active` | Get active outbreak alerts |
| `GET` | `/alerts/detect` | Trigger outbreak detection scan |
| `PUT` | `/alerts/{id}/deactivate` | Deactivate an alert |

### Doctor Dashboard

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/doctor/register` | Register a doctor account |
| `POST` | `/doctor/login` | Login (returns JWT) |
| `GET` | `/doctor/me` | Get current doctor profile |
| `POST` | `/doctor/alerts` | Create & broadcast a health alert |
| `GET` | `/doctor/alerts` | List my alerts |
| `GET` | `/doctor/alerts/public` | Public alerts (no auth) |
| `PUT` | `/doctor/verify/{id}` | Admin: verify a doctor account |

---

## 🌐 Supported Languages

| Code | Language |
|------|----------|
| `en` | English |
| `hi` | Hindi |
| `kn` | Kannada |
| `ta` | Tamil |

---

## 🔒 Security Notes

- JWT tokens are used for doctor authentication. **Change `SECRET_KEY` in production.**
- Twilio credentials are loaded from environment variables — never hard-code them.
- Medical data is stored locally. For production, use encrypted PostgreSQL and enable HTTPS.
- Patient phone numbers are only used for messaging and are not shared externally.

---

## 📄 License

This project is open-source. See [LICENSE](LICENSE) for details.
