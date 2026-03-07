import logging
from typing import Dict, List, Optional
from urllib.parse import quote as urlquote

from fastapi import Depends, FastAPI, File, Form, UploadFile
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .config import get_settings
from .db import Base, engine, get_db
from .models import Report
from .modules import chatbot_module, doctor_dashboard_module, messaging_service, ocr_module, outbreak_detection_module, pdf_export_module, risk_engine, summarizer_module, translation_module, tts_module

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
settings = get_settings()
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Medical Report Interpreter")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatbotRequest(BaseModel):
    session_id: str
    message: str
    symptoms: Optional[List[str]] = None
    risk_level: Optional[str] = "Low"
    fallback: Optional[str] = "Let me know your main symptoms."
    language: Optional[str] = "en"


class DoctorAlertCreate(BaseModel):
    doctor_name: str
    region: str
    title: str
    message: str


class TranslateRequest(BaseModel):
    text: str
    target_language: str


class SendMessageRequest(BaseModel):
    phone: str
    message: str
    test_mode: bool = False


@app.get("/audio/explanation")
def stream_explanation_audio(text: str, language: str = "en", slow: bool = False):
    """Stream audio explanation as MP3.

    Query parameters:
    - text: Text to convert to speech
    - language: Language code (en, hi, kn, ta, te, mr, bn)
    - slow: If true, use slower speech rate for better comprehension
    """
    audio_bytes = tts_module.synthesize_audio_bytes(text, language, slow)
    if not audio_bytes:
        return {"error": "Audio synthesis failed"}
    return StreamingResponse(iter([audio_bytes]), media_type="audio/mpeg")


@app.get("/audio/sentences")
def stream_sentence_audio(text: str, language: str = "en", slow: bool = False):
    """Generate audio for each sentence individually.

    Returns JSON with sentence text and base64-encoded audio for each sentence.
    Useful for interactive sentence-by-sentence playback.
    """
    import base64

    sentences = tts_module.synthesize_sentences(text, language, slow)

    # Encode audio bytes as base64 for JSON transport
    for sentence in sentences:
        audio_bytes = sentence.pop("audio_bytes", b"")
        sentence["audio_base64"] = base64.b64encode(audio_bytes).decode("utf-8")

    return {"sentences": sentences, "total": len(sentences)}


@app.post("/extract-text")
def extract_text_only(file: UploadFile = File(...)):
    """Step 1 — OCR only: extract raw text from an uploaded report file.

    Returns the extracted text, character count, filename and content type
    so the patient / UI can review and correct it before AI analysis.
    This enables the interactive two-step pipeline in the frontend.
    """
    extracted_text = ocr_module.extract_text(file)
    return {
        "extracted_text": extracted_text,
        "char_count": len(extracted_text),
        "filename": file.filename,
        "content_type": file.content_type,
    }


@app.get("/languages")
def list_languages():
    """List all supported translation languages with display names."""
    return {
        "languages": translation_module.list_supported_languages(settings.translation_models)
    }


@app.post("/translate")
def translate_text_endpoint(request: TranslateRequest):
    """Translate text to target language on demand.

    Allows the frontend to re-translate a summary or explanation after
    the report has been processed, without re-running the full pipeline.
    """
    resolved_language = translation_module.normalize_target_language(
        request.target_language,
        settings.translation_models,
    )
    translated = translation_module.translate_text(
        text=request.text,
        target_language=resolved_language,
        translation_models=settings.translation_models,
    )
    return {
        "original_text": request.text,
        "translated_text": translated,
        "target_language": resolved_language,
        "requested_language": request.target_language,
    }


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/process-report")
def process_report(
    file: UploadFile = File(...),
    language: str = Form("en"),
    phone: Optional[str] = Form(None),
    location: str = Form(""),
    symptoms: str = Form(""),
    db: Session = Depends(get_db),
):
    extracted_text = ocr_module.extract_text(file)

    summary_payload = summarizer_module.simplify_report(extracted_text, settings.summarizer_model)
    common_summary = summary_payload["summary"]
    risk_payload = risk_engine.evaluate_risk(extracted_text, [s.strip() for s in symptoms.split(",") if s.strip()])

    resolved_language = translation_module.normalize_target_language(language, settings.translation_models)
    translated_summary = translation_module.translate_text(common_summary, resolved_language, settings.translation_models)
    summary_by_language = {"en": common_summary}
    summary_by_language[resolved_language] = translated_summary
    follow_up_payload = chatbot_module.analyze_report_and_generate_questions(
        report_text=extracted_text,
        risk_level=risk_payload["risk_level"],
        max_questions=4,
    )

    report = Report(
        filename=file.filename,
        text_content=extracted_text,
        simplified_summary=translated_summary,
        risk_level=risk_payload["risk_level"],
        language=resolved_language,
        location=location,
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    symptom_list = [s.strip() for s in symptoms.split(",") if s.strip()]
    if symptom_list:
        outbreak_detection_module.record_symptoms(db, report.id, symptom_list, location)
        outbreak_detection_module.detect_clusters(db)

    # Send messaging alert if phone number provided
    messaging_status = None
    if phone:
        test_mode = settings.tesseract_cmd_path is None  # Auto-detect test mode
        messaging_result = messaging_service.send_message(
            destination=phone,
            body=f"🏥 Medical Report Summary\n\nRisk Level: {risk_payload['risk_level']}\n\n{translated_summary}\n\nRecommendation: {risk_payload.get('recommendation', 'N/A')}",
            test_mode=test_mode
        )
        messaging_status = messaging_result

    audio_url = f"/audio/explanation?text={urlquote(translated_summary)}&language={resolved_language}"

    return {
        "report_id": report.id,
        "summary": translated_summary,
        "summary_common": common_summary,
        "summary_by_language": summary_by_language,
        "language_requested": language,
        "language_resolved": resolved_language,
        "risk": risk_payload,
        "audio_url": audio_url,
        "follow_up": follow_up_payload,
        "messaging_status": messaging_status,
    }


@app.post("/chatbot")
def chatbot(req: ChatbotRequest):
    prompts = chatbot_module.next_questions(req.symptoms or [])

    # Use first detected condition as context for response generation
    conditions = req.symptoms or []
    first_condition = conditions[0] if conditions else None

    response = chatbot_module.generate_response(
        req.message,
        {
            "fallback": req.fallback or "",
            "risk_level": req.risk_level or "Low",
            "current_condition": first_condition,
        },
    )
    insights = chatbot_module.build_chat_insights(
        user_message=req.message,
        symptoms=req.symptoms or [],
        risk_level=req.risk_level or "Low",
    )

    # Translate chatbot response into the requested language
    resolved_lang = translation_module.normalize_target_language(
        req.language or "en", settings.translation_models
    )
    translated_response = response
    if resolved_lang != "en":
        translated_response = translation_module.translate_text(
            response, resolved_lang, settings.translation_models
        )

    audio_url = f"/audio/explanation?text={urlquote(translated_response)}&language={resolved_lang}"

    return {
        "prompts": prompts,
        "response": translated_response,
        "insights": insights,
        "audio_url": audio_url,
        "language": resolved_lang,
    }


@app.get("/outbreaks")
def outbreaks(region: str = "", db: Session = Depends(get_db)):
    clusters = outbreak_detection_module.detect_clusters(db)
    if region:
        clusters = [c for c in clusters if region.lower() in c.get("location", "").lower()]
    return {"clusters": clusters}


@app.post("/doctor/alerts")
def create_doctor_alert(payload: DoctorAlertCreate, db: Session = Depends(get_db)):
    alert = doctor_dashboard_module.create_alert(
        db,
        doctor_name=payload.doctor_name,
        region=payload.region,
        title=payload.title,
        message=payload.message,
    )
    return {"id": alert.id}


@app.get("/doctor/alerts")
def list_doctor_alerts(region: str = "", db: Session = Depends(get_db)):
    alerts = doctor_dashboard_module.list_alerts(db, region=region)
    return {"alerts": alerts}


# ══════════════════════════════════════════════════════════════════════════════
# MESSAGING & TWILIO ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════


@app.get("/messaging/status")
def get_messaging_status():
    """Check if Twilio/messaging is configured and working."""
    is_configured = messaging_service.is_twilio_configured()
    return {
        "configured": is_configured,
        "provider": "Twilio",
        "test_mode_available": True,
        "status": "ready" if is_configured else "not_configured",
        "message": "Twilio is configured and ready to send messages" if is_configured else "Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_FROM_NUMBER in .env to enable messaging",
    }


@app.post("/messaging/send")
def send_test_message(request: SendMessageRequest):
    """Send a test message via SMS/WhatsApp.

    Use test_mode=true to simulate without real credentials.
    """
    result = messaging_service.send_message(
        destination=request.phone,
        body=request.message,
        test_mode=request.test_mode
    )
    return result


@app.get("/messaging/test-history")
def get_messaging_test_history():
    """Get history of simulated messages (test mode only)."""
    history = messaging_service.get_test_message_history()
    return {"history": history, "count": len(history)}


# ══════════════════════════════════════════════════════════════════════════════
# PDF EXPORT ENDPOINT
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/export/pdf/{report_id}")
def export_report_as_pdf(report_id: int, db: Session = Depends(get_db)):
    """Export a processed report as a professional PDF document.

    The PDF includes:
    - Risk assessment with color coding
    - AI-generated simplified summary
    - Original report text
    - Recommendations and alerts
    - Patient information

    Returns PDF file for download.
    """
    # Fetch report from database
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        return {"error": f"Report with ID {report_id} not found"}

    # Reconstruct risk data (if we stored it, otherwise need to recalculate)
    # For now, we'll recalculate from text_content
    risk_payload = risk_engine.evaluate_risk(report.text_content, [])

    # Prepare report data for PDF
    report_data = {
        "summary": report.simplified_summary or "No summary available",
        "risk": risk_payload,
        "audio_url": f"/audio/explanation?text={urlquote(report.simplified_summary or '')}&language={report.language or 'en'}",
    }

    # Prepare patient info
    patient_info = {
        "report_id": f"MR-{report.id:06d}",
        "date": report.created_at.strftime("%B %d, %Y at %H:%M UTC") if report.created_at else "N/A",
        "location": report.location or "Not specified",
        "language": report.language or "en",
    }

    # Generate PDF
    try:
        pdf_bytes = pdf_export_module.generate_report_pdf(
            report_data=report_data,
            report_text=report.text_content,
            patient_info=patient_info
        )

        # Return as downloadable file
        return StreamingResponse(
            iter([pdf_bytes]),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=medical_report_{report.id}.pdf"
            }
        )
    except Exception as e:
        logger.exception("PDF generation failed for report %d", report_id)
        return {"error": f"PDF generation failed: {str(e)}"}

