# 🏥 MedReport AI – Medical Report Interpreter

An AI-powered medical report interpreter with multi-language support, risk assessment, chatbot, and outbreak detection. The full-stack application runs on a single **uvicorn** server (FastAPI backend + HTML frontend).

## Features

- 📄 **OCR & Text Extraction** – Upload PDFs, images, or text files
- 🤖 **AI Summarization** – Plain-language report summaries
- 🌐 **Multi-language Translation** – Hindi, Kannada, Tamil, Telugu, Marathi, Bengali
- ⚕️ **Risk Assessment** – High / Moderate / Low risk scoring with flags
- 🔊 **Text-to-Speech** – Listen to your report summary
- 💬 **AI Chatbot** – Ask health questions about your report
- 🦠 **Outbreak Detection** – Cluster analysis by region
- 👨‍⚕️ **Doctor Alerts** – Dashboard for clinical alerts
- 📥 **PDF Export** – Download professional report PDFs

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

> Install system dependencies if needed:
> - **Tesseract OCR**: `sudo apt install tesseract-ocr` (Linux) or [download installer](https://github.com/UB-Mannheim/tesseract/wiki) (Windows)

### 2. Configure environment (optional)

Copy `.env` and fill in any keys:

```bash
# .env
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_FROM_NUMBER=...
```

### 3. Run the server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Open the app

- **Web UI**: http://localhost:8000/
- **API Docs**: http://localhost:8000/docs

## Sample Reports

Use the included sample files for testing:

| File | Risk Level |
|------|-----------|
| `sample_report_high_risk.txt` | HIGH |
| `sample_report_moderate_risk.txt` | MODERATE |
| `sample_report_low_risk.txt` | LOW |
| `sample_report_pediatric.txt` | LOW-MODERATE |
| `sample_report_diabetes.txt` | MODERATE |

## Project Structure

```
.
├── app/
│   ├── main.py          # FastAPI application + frontend serving
│   ├── config.py        # Settings
│   ├── db.py            # Database setup (SQLite)
│   ├── models.py        # SQLAlchemy models
│   ├── modules/         # Core AI/NLP modules
│   └── static/
│       └── index.html   # Single-page frontend
├── requirements.txt
├── sample_report_*.txt
└── test_*.py
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Web frontend |
| GET | `/health` | Health check |
| POST | `/extract-text` | OCR extraction only |
| POST | `/process-report` | Full AI analysis |
| POST | `/translate` | Translate text |
| GET | `/languages` | Supported languages |
| GET | `/audio/explanation` | TTS audio stream |
| POST | `/chatbot` | AI chatbot |
| GET | `/outbreaks` | Outbreak clusters |
| POST | `/doctor/alerts` | Create doctor alert |
| GET | `/doctor/alerts` | List doctor alerts |
| GET | `/export/pdf/{id}` | Download report PDF |
