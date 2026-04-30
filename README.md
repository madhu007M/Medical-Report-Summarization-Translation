# Sample Medical Reports

This folder contains realistic sample medical reports for testing and demonstrating the AI Medical Report Interpreter platform.

## Available Samples

| File | Risk Level | Conditions | Best For Testing |
|------|-----------|------------|------------------|
| `sample_report_high_risk.txt` | **HIGH** | Hypertensive crisis, poorly controlled diabetes, hypertensive retinopathy | Emergency detection, urgent alerts, high-risk scoring |
| `sample_report_moderate_risk.txt` | **MODERATE** | Upper respiratory infection, borderline elevated BP | Moderate risk classification, symptom chatbot, follow-up recommendations |
| `sample_report_low_risk.txt` | **LOW** | Routine wellness check, mild vitamin D deficiency | Low-risk assessment, preventive care recommendations, wellness advice |
| `sample_report_pediatric.txt` | **LOW-MODERATE** | Pediatric viral fever with rash | Pediatric care, parent education, age-appropriate recommendations |
| `sample_report_diabetes.txt` | **MODERATE** | Type 2 diabetes with complications | Chronic disease management, medication tracking, lifestyle recommendations |

## How to Use These Samples

### Option 1: Upload via Web Interface

1. Start the platform:
   ```bash
   # Terminal 1
   uvicorn backend.app.main:app --reload --port 8000

   # Terminal 2
   streamlit run frontend/streamlit_app.py
   ```

2. Go to http://localhost:8501
3. Click "**Browse files**" in the upload section
4. Select any `.txt` file from the `samples/` folder
5. Follow the 3-step workflow

### Option 2: API Testing via Swagger UI

1. Start backend: `uvicorn backend.app.main:app --reload --port 8000`
2. Visit http://localhost:8000/docs
3. Expand `POST /process-report`
4. Click "**Try it out**"
5. Upload a sample file
6. Set parameters:
   - `language`: `en`, `hi`, `kn`, `ta`, etc.
   - `phone`: `+91234567890` (test mode)
   - `location`: `Mumbai`, `Bangalore`, etc.
   - `symptoms`: `fever, headache, cough`

### Option 3: Automated Testing with curl

```bash
# Test high-risk report
curl -X POST "http://localhost:8000/process-report" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@samples/sample_report_high_risk.txt" \
  -F "language=en" \
  -F "phone=+919876543210" \
  -F "location=Mumbai" \
  -F "symptoms=headache,dizziness,chest pain"

# Test moderate-risk report with Hindi translation
curl -X POST "http://localhost:8000/process-report" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@samples/sample_report_moderate_risk.txt" \
  -F "language=hi" \
  -F "phone=+919876543210" \
  -F "location=Bangalore" \
  -F "symptoms=cough,fever"
```

## Expected Platform Behavior

### For High-Risk Report (`sample_report_high_risk.txt`):

**Expected Risk Score:** 6-8
**Risk Level:** High
**Detected Issues:**
- Blood pressure: 185/115 mmHg (hypertensive crisis)
- Temperature: 103.5°F (high fever)
- Critical terms: "hypertensive crisis", "emergency"

**AI Summary (Example):**
> *"Patient has dangerously high blood pressure (185/115) and high fever (103.5°F). This is a medical emergency requiring immediate hospital care. Symptoms include severe headache, dizziness, blurred vision, and chest discomfort. Immediate hospitalization is recommended for blood pressure control and cardiac monitoring."*

**Expected Alerts:**
- ⚠️ Hypertensive crisis suspected; seek emergency care
- ⚠️ High fever detected
- ⚠️ Symptom reported: chest pain
- ⚠️ Symptom reported: dizziness

**Recommendation:**
> *"Go to the nearest hospital or call emergency services immediately."*

**Chatbot Questions (Examples):**
- "Where exactly is the chest pain located?"
- "Does the pain radiate to your arm, jaw, or back?"
- "Are you experiencing headaches, dizziness, or blurred vision?"

---

### For Moderate-Risk Report (`sample_report_moderate_risk.txt`):

**Expected Risk Score:** 3-5
**Risk Level:** Moderate
**Detected Issues:**
- Blood pressure: 148/92 mmHg (elevated)
- Temperature: 101.2°F (fever)
- WBC: 11,500/μL (mild elevation)

**AI Summary (Example):**
> *"Patient has an upper respiratory tract infection with fever and cough. Blood pressure is slightly elevated and should be monitored. The infection appears to be viral and should resolve with rest, hydration, and symptomatic treatment. Follow up if symptoms worsen or persist beyond 7 days."*

**Expected Alerts:**
- Elevated blood pressure noted
- Fever detected

**Recommendation:**
> *"Schedule an urgent visit with a doctor and monitor symptoms closely."*

---

### For Low-Risk Report (`sample_report_low_risk.txt`):

**Expected Risk Score:** 0-2
**Risk Level:** Low
**Detected Issues:**
- All vitals normal
- Mild vitamin D deficiency (non-urgent)
- Eye strain from screen time

**AI Summary (Example):**
> *"Patient is in good overall health. All vital signs and lab results are within normal range. Mild vitamin D deficiency detected, which can be corrected with supplements and sun exposure. Headaches are related to prolonged screen time. Continue healthy lifestyle and follow preventive care recommendations."*

**Expected Alerts:** None or minimal

**Recommendation:**
> *"Maintain hydration, rest, and follow up with routine care if symptoms persist."*

---

## Testing Different Platform Features

### 1. Multilingual Translation

Upload any sample and select different languages:

```python
# English
language = "en"

# Hindi
language = "hi"

# Kannada
language = "kn"

# Tamil
language = "ta"

# Telugu (if available)
language = "te"
```

**Expected:** Summary should be translated to selected language.

### 2. Voice Explanation

After processing a report, you should receive:
- `audio_url`: `/audio/explanation?text=...&language=en`

**Test:** Click the audio player in UI or visit the URL directly.

### 3. SMS/WhatsApp Messaging (Test Mode)

Provide a phone number in format: `+[country_code][number]`
- SMS: `+919876543210`
- WhatsApp: `whatsapp:+919876543210`

**Expected in test mode:**
- Message simulated (not actually sent)
- Status returned in API response
- Message logged in `/messaging/test-history`

### 4. Symptom Chatbot

After uploading a report, use symptoms field:
- High-risk: `chest pain, dizziness, shortness of breath`
- Moderate: `cough, fever, headache`
- Low: `headache, fatigue`

**Expected:** Chatbot generates condition-specific follow-up questions.

### 5. Outbreak Detection

Upload multiple reports with the same:
- `location`: `Mumbai`
- `symptoms`: `fever, cough`

**Expected:** After 5+ reports (configurable threshold), outbreak cluster detected.

**Test:**
```bash
GET http://localhost:8000/outbreaks?region=Mumbai
```

### 6. Doctor Dashboard

Create a doctor alert:
```json
POST /doctor/alerts
{
  "doctor_name": "Dr. Sharma",
  "region": "Mumbai",
  "title": "Dengue Alert",
  "message": "Increased dengue cases in the area. Please take preventive measures."
}
```

**Expected:** Alert appears in frontend "Doctor Dashboard" tab.

---

## Creating Your Own Test Reports

### Format Guidelines:

```
PATIENT MEDICAL REPORT
======================

Patient Name: [Name]
Age: [Age] years | Gender: [M/F]
Date: [Date]

VITAL SIGNS
-----------
Blood Pressure: [Systolic]/[Diastolic] mmHg
Temperature: [Temp]°F
Heart Rate: [Rate] bpm

CHIEF COMPLAINT
---------------
[Patient's main concern]

CURRENT SYMPTOMS
----------------
[List of symptoms]

IMPRESSION
----------
[Diagnosis]

RECOMMENDATIONS
---------------
[Doctor's advice]
```

### Key Elements for Risk Scoring:

**High Risk Triggers:**
- BP ≥ 180/120 mmHg
- Temperature ≥ 102°F
- Critical terms: sepsis, shock, emergency, crisis
- Symptoms: chest pain, shortness of breath

**Moderate Risk Triggers:**
- BP 140-179/90-119 mmHg
- Temperature 100-101.9°F
- Symptoms: dizziness, vomiting

**Low Risk:**
- BP < 140/90 mmHg
- Temperature < 100°F
- No critical symptoms

---

## Troubleshooting

### Reports Not Being Analyzed Correctly

**Check:**
1. File is plain text (.txt)
2. Contains medical terminology (BP, temperature, symptoms)
3. File encoding is UTF-8
4. No special characters causing parsing issues

### Risk Level Seems Incorrect

**Verify:**
1. Blood pressure values are in the report
2. Temperature values include °F or °C
3. Critical keywords are spelled correctly
4. Symptoms are listed in the symptoms field

### Translation Not Working

**Check:**
1. Backend is running
2. Translation models downloaded (first run takes time)
3. Language code is correct (`en`, `hi`, `kn`, `ta`)
4. Internet connection (for model downloads)

### Audio Not Playing

**Verify:**
1. Audio endpoint returns audio/mpeg
2. URL is properly formatted
3. gTTS has internet access (for synthesis)
4. Browser supports MP3 playback

---

## Quick Demo Script

**5-Minute Demo:**

1. **Start platform** (2 terminals)
2. **Upload high-risk report** → Show emergency alert
3. **Select Hindi** → Show translation
4. **Play audio** → Show voice explanation
5. **Open chatbot tab** → Ask "I have chest pain"
6. **Show doctor dashboard** → Create alert

**10-Minute Demo:**

Add:
- Upload 5 reports with same location → Show outbreak detection
- Test phone number → Show message status
- Compare all 3 risk levels side-by-side

---

## Sample Report Statistics

| Metric | Value |
|--------|-------|
| Total samples | 5 |
| High risk | 1 |
| Moderate risk | 3 |
| Low risk | 1 |
| Average file size | 3-5 KB |
| Languages tested | English (translations to 7 languages supported) |
| Medical domains | General medicine, Pediatrics, Diabetology, Wellness |

---

## Contributing New Samples

To add more test cases:

1. Create a new `.txt` file in `samples/` folder
2. Follow the format guidelines above
3. Include clear vital signs for risk scoring
4. Add realistic medical terminology
5. Name file descriptively: `sample_report_[condition]_[risk].txt`
6. Update this README with the new sample

**Suggestions for Additional Samples:**
- Pregnancy/prenatal care (moderate risk)
- Elderly patient with multiple comorbidities (high risk)
- Sports injury (low risk)
- Mental health assessment (low-moderate risk)
- Cardiac emergency (high risk)

---

## License

These sample reports are fictional and created for testing purposes only. They do not represent real patients or medical advice.

**Medical Disclaimer:** The AI summaries and recommendations generated from these samples should not be used for actual medical decision-making. Always consult a licensed healthcare professional for medical advice.
