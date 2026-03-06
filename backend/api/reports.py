"""
Report upload, OCR extraction, summarization, risk analysis, TTS, and translation.
"""

import os
import uuid
import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, Form, UploadFile, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.config import UPLOAD_DIR, SUPPORTED_LANGUAGES
from backend.models.database import get_db, MedicalReport
from backend.services import (
    ocr_service,
    summarizer,
    translator,
    tts_service,
    risk_service,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/reports", tags=["Reports"])

ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp", ".txt"}


def _validate_extension(filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{suffix}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )
    return suffix[1:]  # return without leading dot


@router.post("/upload", summary="Upload a medical report and process it end-to-end")
async def upload_report(
    file: UploadFile = File(...),
    user_id: Optional[int] = Form(None),
    language: str = Form("en"),
    db: Session = Depends(get_db),
):
    """
    Upload a medical report (PDF / image / text), extract text via OCR,
    generate a plain-language summary, detect risk level, translate into
    supported languages, and generate voice audio.
    """
    file_type = _validate_extension(file.filename)

    # Save uploaded file
    saved_name = f"{uuid.uuid4().hex}_{file.filename}"
    save_path = UPLOAD_DIR / saved_name
    file_bytes = await file.read()
    save_path.write_bytes(file_bytes)
    logger.info("Saved upload: %s", saved_name)

    # Step 1 — OCR / text extraction
    extracted_text = ocr_service.extract_text(file_bytes, file.filename)
    if not extracted_text:
        raise HTTPException(status_code=422, detail="Could not extract text from the uploaded file.")

    # Step 2 — AI summarization
    summary_en = summarizer.summarize(extracted_text)

    # Step 3 — Risk analysis
    risk_result = risk_service.analyse_risk(extracted_text)

    # Step 4 — Translation
    translations = translator.translate_all(summary_en)
    summaries = {"en": summary_en, **translations}

    # Step 5 — TTS (generate audio for the requested language and English)
    audio_paths = tts_service.generate_all_audio(
        {k: v for k, v in summaries.items() if k in ("en", language)}
    )

    # Persist to database
    report = MedicalReport(
        user_id=user_id,
        original_filename=file.filename,
        file_type=file_type,
        extracted_text=extracted_text,
        summary_en=summaries.get("en"),
        summary_hi=summaries.get("hi"),
        summary_kn=summaries.get("kn"),
        summary_ta=summaries.get("ta"),
        risk_level=risk_result["risk_level"],
        risk_score=risk_result["risk_score"],
        risk_details=risk_result["details"],
        audio_path_en=audio_paths.get("en"),
        audio_path_hi=audio_paths.get("hi"),
        audio_path_kn=audio_paths.get("kn"),
        audio_path_ta=audio_paths.get("ta"),
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    return {
        "report_id": report.id,
        "extracted_text": extracted_text,
        "summary": summaries,
        "risk": {
            "level": risk_result["risk_level"],
            "score": risk_result["risk_score"],
            "details": risk_result["details"],
            "recommendations": risk_result["recommendations"],
        },
        "audio": audio_paths,
    }


@router.get("/{report_id}", summary="Get a processed report by ID")
def get_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(MedicalReport).filter(MedicalReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")
    return {
        "id": report.id,
        "filename": report.original_filename,
        "summary": {
            "en": report.summary_en,
            "hi": report.summary_hi,
            "kn": report.summary_kn,
            "ta": report.summary_ta,
        },
        "risk": {
            "level": report.risk_level,
            "score": report.risk_score,
            "details": report.risk_details,
        },
        "created_at": report.created_at.isoformat() if report.created_at else None,
    }


@router.get("/{report_id}/audio/{lang}", summary="Stream audio explanation for a report")
def get_audio(report_id: int, lang: str, db: Session = Depends(get_db)):
    if lang not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail=f"Unsupported language '{lang}'.")
    report = db.query(MedicalReport).filter(MedicalReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")

    audio_path = getattr(report, f"audio_path_{lang}", None)
    if not audio_path or not Path(audio_path).exists():
        # Generate on-demand if not cached
        summary = getattr(report, f"summary_{lang}", None) or report.summary_en
        if not summary:
            raise HTTPException(status_code=404, detail="Summary not available for audio generation.")
        audio_path = tts_service.generate_audio(summary, lang=lang, report_id=report_id)
        if not audio_path:
            raise HTTPException(status_code=500, detail="Audio generation failed.")
        # Update DB
        setattr(report, f"audio_path_{lang}", audio_path)
        db.commit()

    return FileResponse(audio_path, media_type="audio/mpeg", filename=f"report_{report_id}_{lang}.mp3")


@router.get("/", summary="List all reports")
def list_reports(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    reports = db.query(MedicalReport).order_by(MedicalReport.created_at.desc()).offset(skip).limit(limit).all()
    return [
        {
            "id": r.id,
            "filename": r.original_filename,
            "risk_level": r.risk_level,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in reports
    ]
