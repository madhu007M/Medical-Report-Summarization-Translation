"""
Messaging API — send SMS and WhatsApp summaries via Twilio.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.models.database import get_db, MedicalReport, User
from backend.services import messaging_service

router = APIRouter(prefix="/messaging", tags=["Messaging"])


class SendSummaryRequest(BaseModel):
    report_id: int = Field(..., description="Report ID to send")
    phone: str = Field(..., description="Recipient phone number in E.164 format")
    via_whatsapp: bool = Field(False, description="Send via WhatsApp instead of SMS")
    language: str = Field("en", description="Language for the summary")


class BroadcastRequest(BaseModel):
    title: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)
    phone_numbers: list[str] = Field(..., description="List of recipient phone numbers")
    via_whatsapp: bool = Field(False)


@router.post("/send-summary", summary="Send a medical report summary via SMS/WhatsApp")
def send_summary(req: SendSummaryRequest, db: Session = Depends(get_db)):
    report = db.query(MedicalReport).filter(MedicalReport.id == req.report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")

    summary = (
        getattr(report, f"summary_{req.language}", None)
        or report.summary_en
        or "No summary available."
    )
    risk_level = report.risk_level or "Unknown"

    result = messaging_service.send_report_summary(
        phone=req.phone,
        summary=summary,
        risk_level=risk_level,
        via_whatsapp=req.via_whatsapp,
    )
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "Messaging failed."))

    return {"message": "Summary sent successfully.", "sid": result["sid"]}


@router.post("/broadcast", summary="Broadcast a health alert to multiple recipients")
def broadcast(req: BroadcastRequest):
    results = messaging_service.broadcast_alert(
        phone_numbers=req.phone_numbers,
        title=req.title,
        message=req.message,
        via_whatsapp=req.via_whatsapp,
    )
    success_count = sum(1 for r in results if r.get("success"))
    return {
        "total": len(results),
        "success": success_count,
        "failed": len(results) - success_count,
        "results": results,
    }
