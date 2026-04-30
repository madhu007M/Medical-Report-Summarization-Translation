# 🚀 Quick Start Guide - AI Medical Report Interpreter

## ⚡ Fastest Way to Run (Recommended)

### Option 1: Run Everything Together
```bash
# Double-click this file:
START_PLATFORM.bat
```
This will automatically start both backend and frontend in separate windows.

---

## 📋 Manual Start (Two Terminals)

### Terminal 1 - Backend Server

```bash
# Double-click:
start_backend.bat

# Or manually:
.venv\Scripts\activate
uvicorn backend.app.main:app --reload --port 8000
```

**Backend will be running at:**
- Main API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Terminal 2 - Frontend

```bash
# Double-click:
start_frontend.bat

# Or manually:
.venv\Scripts\activate
streamlit run frontend/streamlit_app.py
```

**Frontend will open at:**
- http://localhost:8501

---

## 🎯 First-Time Setup Checklist

✅ **Already Done:**
- [x] Virtual environment created
- [x] Dependencies installed
- [x] Database configured
- [x] Twilio phone number configured (+14174793723)

⚠️ **Still Needed (Optional):**
- [ ] Twilio Account SID (for real SMS)
- [ ] Twilio Auth Token (for real SMS)

**Note:** Platform works in **test mode** without Twilio credentials!

---

## 🧪 Testing the Platform

### 1. Upload a Sample Report

Once the platform is running:

1. Go to http://localhost:8501
2. Click **"Browse files"**
3. Upload: `samples/sample_report_high_risk.txt`
4. Select language (English, Hindi, etc.)
5. Click **"🔍 Extract Text from Report"**
6. Review text, then click **"🤖 Analyze with AI"**

### 2. See the Results

You should see:
- **Risk Level:** 🔴 High (Emergency)
- **Simplified Summary** in plain language
- **Voice Explanation** (audio player)
- **Recommendations** for next steps
- **PDF Download** button

### 3. Try Different Features

**Voice Explanation:**
- Click the audio player to hear the summary
- Try "Slow mode" checkbox
- Try "Sentence-by-sentence" mode

**Translate:**
- Select a different language from dropdown
- Click "🔄 Translate" button
- Audio updates automatically

**Dark Mode:**
- Click 🌙 button in sidebar
- Toggle between light/dark themes

**Compare Reports:**
- Go to "📊 Report History" tab
- Upload multiple reports
- See risk trends over time

---

## 📱 Testing SMS/WhatsApp (Test Mode)

**Without Twilio credentials,** the platform will simulate messages:

1. Upload a report
2. Enter phone number: `+919876543210`
3. Process the report
4. Check message status in response

To see simulated messages:
```
http://localhost:8000/messaging/test-history
```

---

## 🔧 Troubleshooting

### Backend Won't Start

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Fix:**
```bash
.venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend Won't Start

**Error:** `command not found: streamlit`

**Fix:**
```bash
.venv\Scripts\activate
pip install streamlit
```

### Port Already in Use

**Error:** `Address already in use: 8000`

**Fix:**
```bash
# Find and kill the process
netstat -ano | findstr :8000
taskkill /PID <pid_number> /F

# Or use a different port
uvicorn backend.app.main:app --reload --port 8001
```

### Models Taking Long to Download

**First run downloads ~5GB of AI models:**
- BART summarization model
- Translation models for 7 languages

**This is normal!** Subsequent runs will be instant.

**Progress:**
Watch the backend terminal - you'll see download progress bars.

### Database Errors

**Error:** `no such table: reports`

**Fix:**
```bash
# Delete and recreate database
del health_platform.db

# Restart backend - database will auto-create
start_backend.bat
```

---

## 📊 What Each Tab Does

### Tab 1: 📄 Report Upload
- **3-step workflow:** Upload → Review → Analyze
- Upload PDF, images, or text files
- Edit extracted text before analysis
- Get AI summary, risk score, and recommendations

### Tab 2: 💬 Symptom Chatbot
- Interactive health Q&A
- Context-aware follow-up questions
- Symptom-based guidance

### Tab 3: 🩺 Doctor Dashboard
- Post regional health alerts
- View outbreak clusters
- Monitor disease trends

### Tab 4: 📊 Report History (NEW!)
- Upload multiple reports
- Compare results over time
- Visual trend charts
- Batch PDF export

---

## 🎨 UI Features

### Dark Mode
- Click 🌙/☀️ in sidebar
- Saves your preference

### Audio Controls
- **Full summary:** Complete audio playback
- **Sentence mode:** Play one sentence at a time
- **Slow mode:** Slower speech for clarity
- **Download:** Save MP3 file

### PDF Export
- Professional multi-page PDFs
- Color-coded risk levels
- Includes original + AI analysis
- Ready to share with doctors

---

## 📈 Sample Reports Available

Try these in `samples/` folder:

| File | Risk Level | Best For Testing |
|------|-----------|------------------|
| `sample_report_high_risk.txt` | 🔴 HIGH | Emergency detection |
| `sample_report_moderate_risk.txt` | 🟠 MODERATE | Standard workflow |
| `sample_report_low_risk.txt` | 🟢 LOW | Wellness checks |
| `sample_report_pediatric.txt` | 🟠 LOW-MOD | Pediatric cases |
| `sample_report_diabetes.txt` | 🟠 MODERATE | Chronic disease tracking |

---

## 🌍 Supported Languages

Translation available for:
- 🇬🇧 English
- 🇮🇳 Hindi (हिन्दी)
- 🇮🇳 Kannada (ಕನ್ನಡ)
- 🇮🇳 Tamil (தமிழ்)
- 🇮🇳 Telugu (తెలుగు)
- 🇮🇳 Marathi (मराठी)
- 🇮🇳 Bengali (বাংলা)

Voice explanations work in **100+ languages** via gTTS!

---

## 🔗 Important URLs

**Frontend:**
- Main App: http://localhost:8501

**Backend:**
- API Root: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

**Special Endpoints:**
- Messaging Status: http://localhost:8000/messaging/status
- Test History: http://localhost:8000/messaging/test-history

---

## 💾 Stopping the Platform

### If using START_PLATFORM.bat:
1. Close both terminal windows
2. Or press `Ctrl+C` in each window

### Manual stop:
1. Press `Ctrl+C` in backend terminal
2. Press `Ctrl+C` in frontend terminal

---

## 📚 Next Steps

1. **Try all sample reports** to see different risk levels
2. **Test dark mode** and PDF export
3. **Upload multiple reports** to see trend analysis
4. **Configure Twilio** for real SMS (optional)
5. **Read full documentation:**
   - `README.md` - Platform overview
   - `TWILIO_SETUP_GUIDE.md` - SMS setup
   - `ENHANCEMENTS_SUMMARY.md` - New features
   - `samples/README.md` - Sample report guide

---

## ⚡ Quick Command Reference

```bash
# Start platform (all-in-one)
START_PLATFORM.bat

# Start backend only
start_backend.bat

# Start frontend only
start_frontend.bat

# Run tests
.venv\Scripts\activate
pytest tests/ -v

# Check messaging status
curl http://localhost:8000/messaging/status

# Upload test report
# (Use Swagger UI at http://localhost:8000/docs)
```

---

## 🎉 You're Ready!

**Just run:** `START_PLATFORM.bat`

The platform will open automatically in your browser at http://localhost:8501

**Have fun exploring your AI Medical Report Interpreter!** 🏥✨

---

## 📞 Support

- Check `TROUBLESHOOTING.md` for common issues
- Review API docs at http://localhost:8000/docs
- All features work in test mode (no external services needed)

**Project is 100% functional and ready to use!** 🚀
