"""
Streamlit Frontend — AI Medical Report Interpreter & Community Health Platform

Run with:
    streamlit run frontend/app.py
"""

import io
import os
import json
import requests
import streamlit as st
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")

LANG_OPTIONS = {
    "English": "en",
    "Hindi": "hi",
    "Kannada": "kn",
    "Tamil": "ta",
}

RISK_COLORS = {
    "Low": "#28a745",
    "Moderate": "#ffc107",
    "High": "#dc3545",
    "Unknown": "#6c757d",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _api(method: str, path: str, **kwargs):
    """Make an API call and return (response | None, error_str | None)."""
    url = f"{API_BASE}{path}"
    try:
        resp = getattr(requests, method)(url, timeout=120, **kwargs)
        if resp.status_code < 400:
            return resp, None
        return None, resp.json().get("detail", resp.text)
    except requests.exceptions.ConnectionError:
        return None, f"Cannot connect to backend at {API_BASE}. Is it running?"
    except Exception as exc:
        return None, str(exc)


def _badge(text: str, color: str) -> str:
    return (
        f'<span style="background:{color};color:white;padding:4px 12px;'
        f'border-radius:12px;font-weight:bold;">{text}</span>'
    )


# ---------------------------------------------------------------------------
# Page setup
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="AI Medical Report Interpreter",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------

st.sidebar.image(
    "https://img.icons8.com/color/96/000000/medical-history.png",
    width=80,
)
st.sidebar.title("🏥 MedReport AI")
st.sidebar.caption("AI-powered medical report interpretation")

page = st.sidebar.radio(
    "Navigate",
    [
        "📄 Upload Report",
        "💬 Symptom Chatbot",
        "🌍 Community Alerts",
        "👨‍⚕️ Doctor Dashboard",
        "ℹ️ About",
    ],
)

st.sidebar.divider()
lang_name = st.sidebar.selectbox("🌐 Preferred Language", list(LANG_OPTIONS.keys()), index=0)
lang_code = LANG_OPTIONS[lang_name]


# ===========================================================================
# PAGE 1 — Upload Report
# ===========================================================================

if page == "📄 Upload Report":
    st.title("📄 Medical Report Interpreter")
    st.caption("Upload your report (PDF, image, or text) to get a plain-language explanation.")

    col_upload, col_info = st.columns([2, 1])

    with col_upload:
        uploaded = st.file_uploader(
            "Upload Medical Report",
            type=["pdf", "jpg", "jpeg", "png", "bmp", "tiff", "webp", "txt"],
            help="Supported formats: PDF, JPEG, PNG, BMP, TIFF, WEBP, TXT",
        )

    with col_info:
        st.info(
            "**What happens to your report?**\n\n"
            "1. Text is extracted using OCR\n"
            "2. AI summarises in plain language\n"
            "3. Risk level is assessed\n"
            "4. Summary translated to your language\n"
            "5. Voice audio generated for you\n"
        )

    if uploaded:
        with st.spinner("Processing your report… this may take a minute."):
            resp, err = _api(
                "post",
                "/reports/upload",
                files={"file": (uploaded.name, uploaded.getvalue(), uploaded.type)},
                data={"language": lang_code},
            )

        if err:
            st.error(f"❌ Error: {err}")
        else:
            data = resp.json()
            report_id = data["report_id"]
            st.session_state["report_id"] = report_id
            st.session_state["report_data"] = data

            st.success(f"✅ Report processed! (Report ID: {report_id})")

    # Display results if available
    if "report_data" in st.session_state:
        data = st.session_state["report_data"]
        report_id = st.session_state["report_id"]

        st.divider()

        # Risk badge
        risk = data.get("risk", {})
        risk_level = risk.get("level", "Unknown")
        risk_color = RISK_COLORS.get(risk_level, "#6c757d")
        st.markdown(
            f"### Risk Assessment: {_badge(risk_level, risk_color)}",
            unsafe_allow_html=True,
        )

        # Risk score bar
        risk_score = risk.get("score", 0)
        st.progress(min(risk_score / 15, 1.0), text=f"Risk Score: {risk_score:.1f}/15")

        # Recommendations
        recommendations = risk.get("recommendations", [])
        if recommendations:
            with st.expander("📋 Recommendations", expanded=True):
                for rec in recommendations:
                    st.write(f"• {rec}")

        st.divider()

        # Summary
        st.subheader("📝 Patient-Friendly Summary")
        summaries = data.get("summary", {})
        tab_labels = [name for name in LANG_OPTIONS.keys() if LANG_OPTIONS[name] in summaries]
        tabs = st.tabs(tab_labels)

        for tab, name in zip(tabs, tab_labels):
            lc = LANG_OPTIONS[name]
            with tab:
                st.write(summaries.get(lc, "_Translation not available._"))

                # Audio player
                audio_url = f"{API_BASE}/reports/{report_id}/audio/{lc}"
                audio_paths = data.get("audio", {})
                if audio_paths.get(lc):
                    st.audio(audio_url, format="audio/mp3")
                else:
                    if st.button(f"🔊 Generate audio ({name})", key=f"audio_{lc}"):
                        with st.spinner("Generating audio…"):
                            ar, aerr = _api("get", f"/reports/{report_id}/audio/{lc}")
                        if aerr:
                            st.error(aerr)
                        else:
                            st.audio(audio_url, format="audio/mp3")

        st.divider()

        # Vital parameters detail
        details = risk.get("details", {})
        if details:
            with st.expander("🔬 Detailed Risk Parameter Analysis"):
                for key, val in details.items():
                    if isinstance(val, dict):
                        level = val.get("level", "")
                        color = RISK_COLORS.get(level, "#6c757d")
                        st.markdown(
                            f"**{key.upper()}**: {val.get('note', '')} "
                            f"{_badge(level, color)}",
                            unsafe_allow_html=True,
                        )

        # SMS / WhatsApp
        st.divider()
        st.subheader("📱 Receive via SMS / WhatsApp")
        phone = st.text_input("Your phone number (E.164 format, e.g. +919876543210)")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📩 Send SMS") and phone:
                r, e = _api(
                    "post",
                    "/messaging/send-summary",
                    json={"report_id": report_id, "phone": phone, "language": lang_code},
                )
                if e:
                    st.error(e)
                else:
                    st.success("SMS sent!")
        with col2:
            if st.button("💬 Send WhatsApp") and phone:
                r, e = _api(
                    "post",
                    "/messaging/send-summary",
                    json={"report_id": report_id, "phone": phone, "language": lang_code, "via_whatsapp": True},
                )
                if e:
                    st.error(e)
                else:
                    st.success("WhatsApp message sent!")

        # Start chatbot CTA
        st.divider()
        if st.button("💬 Start Symptom Chatbot for this Report"):
            st.session_state["chat_report_id"] = report_id
            st.rerun()


# ===========================================================================
# PAGE 2 — Symptom Chatbot
# ===========================================================================

elif page == "💬 Symptom Chatbot":
    st.title("💬 Symptom-Based Medical Chatbot")
    st.caption("An AI assistant that asks follow-up questions to better understand your condition.")

    report_id = st.session_state.get("chat_report_id") or st.session_state.get("report_id")

    if not report_id:
        report_id_input = st.number_input("Enter Report ID to start chatting", min_value=1, step=1)
        if st.button("Start Chat") and report_id_input:
            report_id = int(report_id_input)
            st.session_state["chat_report_id"] = report_id
    else:
        st.info(f"Chatting about **Report ID: {report_id}**")

    if report_id:
        # Initialise session
        if "chat_session_id" not in st.session_state:
            with st.spinner("Starting chat session…"):
                r, e = _api("get", f"/chatbot/start/{report_id}")
            if e:
                st.error(e)
            else:
                d = r.json()
                st.session_state["chat_session_id"] = d["session_id"]
                st.session_state["chat_history"] = d["history"]

        # Display history
        history = st.session_state.get("chat_history", [])
        for msg in history:
            role = msg["role"]
            with st.chat_message("assistant" if role == "assistant" else "user"):
                st.write(msg["content"])

        # Input box
        user_input = st.chat_input("Type your message here…")
        if user_input:
            with st.chat_message("user"):
                st.write(user_input)

            with st.spinner("Thinking…"):
                r, e = _api(
                    "post",
                    "/chatbot/chat",
                    json={
                        "report_id": report_id,
                        "message": user_input,
                        "session_id": st.session_state.get("chat_session_id"),
                    },
                )
            if e:
                st.error(e)
            else:
                d = r.json()
                st.session_state["chat_history"] = d["history"]
                st.session_state["chat_session_id"] = d["session_id"]
                with st.chat_message("assistant"):
                    st.write(d["response"])
                st.rerun()

        if st.button("🔄 Reset Chat"):
            for key in ["chat_session_id", "chat_history", "chat_report_id"]:
                st.session_state.pop(key, None)
            st.rerun()


# ===========================================================================
# PAGE 3 — Community Alerts
# ===========================================================================

elif page == "🌍 Community Alerts":
    st.title("🌍 Community Health Alerts & Outbreak Monitor")

    tab1, tab2 = st.tabs(["📊 Active Alerts", "📝 Log Symptoms"])

    with tab1:
        region_filter = st.text_input("Filter by region (optional)", "")
        refresh_alerts = st.button("🔄 Refresh Alerts")
        # Load alerts on initial page render or when refresh is clicked
        if "alerts_cache" not in st.session_state or refresh_alerts:
            params = f"?region={region_filter}" if region_filter else ""
            r, e = _api("get", f"/alerts/active{params}")
            if e:
                st.error(e)
                st.session_state["alerts_cache"] = []
            else:
                st.session_state["alerts_cache"] = r.json().get("alerts", [])

        alerts_data = st.session_state.get("alerts_cache", [])
        if not alerts_data:
            st.info("No active outbreak alerts at this time. ✅")
        else:
            for alert in alerts_data:
                severity = alert.get("severity", "Watch")
                color = {"Watch": "#ffc107", "Warning": "#fd7e14", "Emergency": "#dc3545"}.get(severity, "#6c757d")
                with st.expander(f"🦠 {alert['disease'].title()} — {alert['region']} [{severity}]"):
                    st.markdown(
                        f"**Cases:** {alert['case_count']} | "
                        f"**Severity:** {_badge(severity, color)}",
                        unsafe_allow_html=True,
                    )
                    st.write(alert.get("message", ""))
                    st.caption(f"Detected: {alert.get('created_at', 'N/A')}")

        # Doctor public alerts
        st.divider()
        st.subheader("📢 Doctor Health Bulletins")
        r, e = _api("get", "/doctor/alerts/public")
        if e:
            st.error(e)
        else:
            doc_alerts = r.json() if r else []
            if not doc_alerts:
                st.info("No bulletins posted yet.")
            else:
                for da in doc_alerts:
                    alert_type = da.get("alert_type", "awareness")
                    icon = {"awareness": "ℹ️", "prevention": "🛡️", "emergency": "🚨"}.get(alert_type, "📢")
                    with st.expander(f"{icon} {da['title']}"):
                        st.write(da["message"])
                        st.caption(f"Region: {da.get('region', 'All')} | {da.get('created_at', 'N/A')[:10]}")

    with tab2:
        st.subheader("📝 Report Your Symptoms")
        st.caption("Help monitor community health by reporting your symptoms anonymously.")

        col_a, col_b = st.columns(2)
        with col_a:
            region = st.text_input("Your region / city")
        with col_b:
            lat = st.number_input("Latitude (optional)", value=0.0, format="%.4f")
            lon = st.number_input("Longitude (optional)", value=0.0, format="%.4f")

        COMMON_SYMPTOMS = [
            "Fever", "Cough", "Fatigue", "Headache", "Body Ache",
            "Rash", "Vomiting", "Diarrhoea", "Joint Pain", "Chills",
            "Difficulty Breathing", "Chest Pain", "Loss of Taste", "Sore Throat",
        ]
        selected_symptoms = st.multiselect("Select your symptoms", COMMON_SYMPTOMS)
        custom_symptom = st.text_input("Add other symptoms (comma-separated)")

        all_symptoms = selected_symptoms + [s.strip() for s in custom_symptom.split(",") if s.strip()]

        if st.button("📤 Submit Symptoms") and all_symptoms:
            r, e = _api(
                "post",
                "/alerts/log-symptoms",
                json={
                    "symptoms": [s.lower() for s in all_symptoms],
                    "region": region or None,
                    "location_lat": lat or None,
                    "location_lon": lon or None,
                },
            )
            if e:
                st.error(e)
            else:
                d = r.json()
                st.success("✅ Symptoms logged. Thank you for helping monitor community health.")
                if d.get("inferred_disease"):
                    st.info(f"🦠 Possible condition detected: **{d['inferred_disease'].title()}**")
                if d.get("new_alerts_generated", 0) > 0:
                    st.warning(f"⚠️ {d['new_alerts_generated']} new outbreak alert(s) generated in your region.")


# ===========================================================================
# PAGE 4 — Doctor Dashboard
# ===========================================================================

elif page == "👨‍⚕️ Doctor Dashboard":
    st.title("👨‍⚕️ Doctor Dashboard")

    doctor_tab = st.tabs(["🔑 Login / Register", "📢 Post Alert", "📋 My Alerts"])

    # --- Login / Register ---
    with doctor_tab[0]:
        auth_mode = st.radio("", ["Login", "Register"], horizontal=True)

        if auth_mode == "Login":
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            if st.button("🔐 Login"):
                r, e = _api(
                    "post",
                    "/doctor/login",
                    data={"username": email, "password": password},
                )
                if e:
                    st.error(f"Login failed: {e}")
                else:
                    token = r.json()["access_token"]
                    st.session_state["doctor_token"] = token
                    # Fetch profile
                    pr, pe = _api("get", "/doctor/me", headers={"Authorization": f"Bearer {token}"})
                    if pr:
                        st.session_state["doctor_profile"] = pr.json()
                    st.success(f"Welcome, {st.session_state['doctor_profile'].get('name', 'Doctor')}!")
                    st.rerun()

        else:  # Register
            name = st.text_input("Full Name")
            email = st.text_input("Email")
            password = st.text_input("Password (min 8 chars)", type="password")
            region = st.text_input("Region / City")
            specialization = st.text_input("Specialization (e.g., General Physician)")
            if st.button("📝 Register"):
                r, e = _api(
                    "post",
                    "/doctor/register",
                    json={
                        "name": name,
                        "email": email,
                        "password": password,
                        "region": region,
                        "specialization": specialization,
                    },
                )
                if e:
                    st.error(e)
                else:
                    st.success(r.json().get("message", "Registered! Awaiting verification."))

        if "doctor_token" in st.session_state:
            profile = st.session_state.get("doctor_profile", {})
            st.divider()
            st.success(
                f"✅ Logged in as **{profile.get('name')}** "
                f"({profile.get('specialization', 'Doctor')}, {profile.get('region', 'N/A')})"
            )
            if st.button("🚪 Logout"):
                st.session_state.pop("doctor_token", None)
                st.session_state.pop("doctor_profile", None)
                st.rerun()

    # --- Post Alert ---
    with doctor_tab[1]:
        if "doctor_token" not in st.session_state:
            st.warning("Please log in first.")
        else:
            st.subheader("📢 Broadcast a Health Alert")
            title = st.text_input("Alert Title")
            message = st.text_area("Alert Message", height=150)
            alert_region = st.text_input("Target Region (leave blank for all)")
            alert_type = st.selectbox("Alert Type", ["awareness", "prevention", "emergency"])
            broadcast_sms = st.checkbox("Also send SMS to registered users in this region")

            if st.button("🚀 Post Alert"):
                if not title or not message:
                    st.error("Title and message are required.")
                else:
                    token = st.session_state["doctor_token"]
                    r, e = _api(
                        "post",
                        "/doctor/alerts",
                        json={
                            "title": title,
                            "message": message,
                            "region": alert_region or None,
                            "alert_type": alert_type,
                            "broadcast_sms": broadcast_sms,
                        },
                        headers={"Authorization": f"Bearer {token}"},
                    )
                    if e:
                        st.error(e)
                    else:
                        d = r.json()
                        st.success(f"✅ Alert posted! (ID: {d['alert_id']})")
                        if d.get("sms_broadcast"):
                            sms = d["sms_broadcast"]
                            st.info(f"📱 SMS sent to {sms['sent']}/{sms['total']} users.")

    # --- My Alerts ---
    with doctor_tab[2]:
        if "doctor_token" not in st.session_state:
            st.warning("Please log in first.")
        else:
            token = st.session_state["doctor_token"]
            r, e = _api("get", "/doctor/alerts", headers={"Authorization": f"Bearer {token}"})
            if e:
                st.error(e)
            else:
                my_alerts = r.json() if r else []
                if not my_alerts:
                    st.info("You haven't posted any alerts yet.")
                else:
                    for a in my_alerts:
                        with st.expander(f"📢 {a['title']} ({a.get('created_at', '')[:10]})"):
                            st.write(a["message"])
                            st.caption(
                                f"Type: {a['alert_type']} | Region: {a.get('region', 'All')}"
                            )


# ===========================================================================
# PAGE 5 — About
# ===========================================================================

elif page == "ℹ️ About":
    st.title("ℹ️ About This Platform")
    st.markdown(
        """
## AI Medical Report Interpreter & Community Health Communication Platform

This platform helps patients understand complex medical reports regardless of language
or literacy level, and supports community health monitoring.

### 🔧 Key Features

| Feature | Technology |
|---------|------------|
| **OCR Text Extraction** | EasyOCR / Tesseract / pdfplumber |
| **AI Summarization** | BART (facebook/bart-large-cnn) via HuggingFace |
| **Risk Detection** | Rule-based thresholds (glucose, BP, Hb, WBC, SpO2) |
| **Multilingual Translation** | MarianMT (Helsinki-NLP) — English, Hindi, Kannada, Tamil |
| **Voice Explanation** | gTTS (Google Text-to-Speech) |
| **Symptom Chatbot** | Rule-based NLP with medical follow-up questions |
| **SMS / WhatsApp** | Twilio APIs |
| **Outbreak Detection** | Symptom clustering + disease inference |
| **Doctor Dashboard** | JWT-authenticated REST API |
| **Backend** | FastAPI + SQLAlchemy + SQLite/PostgreSQL |
| **Frontend** | Streamlit |

### 🗂️ Architecture

```
Report Upload → OCR Extraction → AI Summarization → Risk Detection
     → Translation (HI/KN/TA) → TTS Audio → Chatbot Interaction
          → SMS/WhatsApp Alerts → Community Outbreak Monitor
                    → Doctor Dashboard Broadcasts
```

### 🚀 Getting Started

```bash
# Install dependencies
pip install -r requirements.txt

# Start the backend
uvicorn backend.main:app --reload --port 8000

# Start the frontend (in another terminal)
streamlit run frontend/app.py
```

### 📞 Contact & Contributions

Open an issue or pull request on GitHub.
        """,
        unsafe_allow_html=False,
    )
