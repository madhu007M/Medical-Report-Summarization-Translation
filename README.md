# AI Medical Report Interpreter

A FastAPI-based backend for summarizing and translating medical reports using AI.

---

## Prerequisites

- **Python 3.9+** – [Download](https://www.python.org/downloads/)
- **pip** (bundled with Python)

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/madhu007M/Medical-Report-Summarization-Translation.git
cd Medical-Report-Summarization-Translation
```

### 2. Create and activate a virtual environment

**Windows:**
```cmd
python -m venv .venv
.venv\Scripts\activate
```

**Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Running the Project

### Option A — Use the start script

**Windows:**
```cmd
start_backend.bat
```

**Linux / macOS:**
```bash
chmod +x start_backend.sh
./start_backend.sh
```

### Option B — Run manually

Make sure your virtual environment is activated, then:

```bash
uvicorn backend.app.main:app --reload --port 8000
```

---

## Accessing the Application

| Resource | URL |
|---|---|
| Backend API | <http://localhost:8000> |
| Interactive API Docs (Swagger UI) | <http://localhost:8000/docs> |
| Alternative API Docs (ReDoc) | <http://localhost:8000/redoc> |

---

## Project Structure

```
Medical-Report-Summarization-Translation/
├── backend/
│   └── app/
│       └── main.py          # FastAPI application entry point
├── requirements.txt         # Python dependencies
├── start_backend.bat        # Windows startup script
├── start_backend.sh         # Linux/macOS startup script
└── README.md
```

---

## Stopping the Server

Press **Ctrl + C** in the terminal where the server is running.
