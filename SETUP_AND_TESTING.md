# Medical Platform Setup & Deployment Guide

## Part 1: Configuration (Tesseract & Twilio)

### Tesseract OCR Setup

#### Windows
1. Download installer from: https://github.com/tesseract-ocr/tesseract/wiki/Downloads
2. Run installer (default: `C:\Program Files\Tesseract-OCR\tesseract.exe`)
3. Set environment variable in `.env`:
   ```
   TESSERACT_CMD_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
   ```

#### Linux
```bash
sudo apt-get install tesseract-ocr
# No need to set TESSERACT_CMD_PATH, it's on PATH by default
```

#### macOS
```bash
brew install tesseract
# No need to set TESSERACT_CMD_PATH, it's on PATH by default
```

### Twilio Configuration

1. Sign up at https://www.twilio.com/
2. Get credentials from Twilio Console:
   - **Account SID**: Settings → General
   - **Auth Token**: Settings → General
   - **Phone Number**: Phone Numbers → Manage Numbers → Active Numbers
3. Create `.env` file in project root:
   ```
   TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   TWILIO_AUTH_TOKEN=your_auth_token_here
   TWILIO_FROM_NUMBER=+1234567890
   ```

### Environment File Template

Copy `.env.example` to `.env` and customize:
```bash
cp .env.example .env
# Edit .env with your values
```

## Part 2: Running Tests

### Install Test Dependencies
```bash
pip install -r requirements.txt
```

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Test Suite
```bash
# OCR module tests
pytest tests/test_ocr_module.py -v

# Summarizer tests
pytest tests/test_summarizer_module.py -v

# Translation tests
pytest tests/test_translation_module.py -v

# Risk engine tests
pytest tests/test_risk_engine.py -v

# API endpoint tests
pytest tests/test_api_endpoints.py -v

# TTS module tests
pytest tests/test_tts_module.py -v
```

### Generate Coverage Report
```bash
pytest tests/ --cov=backend --cov-report=html
# Open htmlcov/index.html in browser
```

## Part 3: Running the Application

### 1. Start Backend (FastAPI)
```bash
uvicorn backend.app.main:app --reload --port 8000
```

Backend will be available at: `http://localhost:8000`
- API docs: `http://localhost:8000/docs` (interactive Swagger UI)
- ReDoc: `http://localhost:8000/redoc`

### 2. Start Frontend (in separate terminal)
```bash
streamlit run frontend/streamlit_app.py
```

Frontend will open at: `http://localhost:8501`

## Part 4: Audio Streaming (HTTP Instead of Filesystem)

### What Changed
- **Old**: Generated MP3 files to disk, returned file path
- **New**: Generate audio bytes and stream via HTTP endpoint

### API Endpoint
```
GET /audio/explanation?text={text}&language={language}
```

Returns: MP3 audio stream (audio/mpeg)

### Frontend Usage
```python
full_url = f"{BACKEND_URL}{audio_url}"
st.audio(full_url, format="audio/mp3")
```

### Benefits
- ✅ No disk I/O required
- ✅ Works across network
- ✅ Scalable (no file cleanup needed)
- ✅ Better for cloud deployments

## Part 5: Testing Workflows

### Test OCR with Real Image
1. Place test image in `tests/fixtures/sample.png`
2. Run: `pytest tests/test_ocr_module.py::TestOCRModule::test_extract_text_image -v`

### Test Report Processing E2E
```bash
# Upload a sample PDF via Streamlit
streamlit run frontend/streamlit_app.py
# Use the UI to upload a report
```

### Test Messaging (Twilio)
1. Ensure Twilio credentials are in `.env`
2. Run: `pytest tests/test_api_endpoints.py::TestAPIEndpoints::test_process_report_endpoint -v`
3. SMS will be sent to `TWILIO_FROM_NUMBER` (if configured correctly)

### Manual API Testing with cURL
```bash
# Health check
curl http://localhost:8000/health

# Get audio stream
curl http://localhost:8000/audio/explanation?text=Fever&language=en --output explanation.mp3

# Get doctor alerts
curl http://localhost:8000/doctor/alerts

# List outbreaks
curl http://localhost:8000/outbreaks
```

## Part 6: Docker Deployment (Optional)

Create `Dockerfile`:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t medical-platform .
docker run -p 8000:8000 -e DATABASE_URL=sqlite:///health.db medical-platform
```

## Part 7: Production Checklist

- [ ] Set `DATABASE_URL` to PostgreSQL for multi-user
- [ ] Enable HTTPS (use Nginx reverse proxy)
- [ ] Configure CORS for frontend domain
- [ ] Set up logging (CloudWatch, Stackdriver, etc.)
- [ ] Add rate limiting to API endpoints
- [ ] Enable CSRF protection for Streamlit
- [ ] Validate and sanitize all user inputs
- [ ] Implement authentication for doctor dashboard
- [ ] Regular backups of database
- [ ] Monitor model memory usage (Transformers can be large)

## Troubleshooting

### Tesseract Not Found
```
Error: tesseract is not installed or it's not in your PATH
```
**Solution**: Ensure Tesseract is installed and `TESSERACT_CMD_PATH` is correct.

### Models Not Downloading
```
Error: Connection timeout downloading model
```
**Solution**: Models auto-download on first use. Ensure internet connection and sufficient disk space (~5GB).

### Twilio SMS Not Sending
```
Warning: Twilio credentials missing; skipping SMS/WhatsApp send
```
**Solution**: Add valid `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM_NUMBER` to `.env`.

### Port Already in Use
```
ERROR: Address already in use
```
**Solution**: 
```bash
uvicorn backend.app.main:app --port 8001  # Use different port
```

## Additional Resources

- FastAPI Docs: https://fastapi.tiangolo.com/
- Streamlit Docs: https://docs.streamlit.io/
- Hugging Face Transformers: https://huggingface.co/docs/transformers/
- Pytest Docs: https://docs.pytest.org/
- Twilio Docs: https://www.twilio.com/docs/
