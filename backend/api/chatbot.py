"""
Chatbot API — symptom-based follow-up conversation.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

from backend.models.database import get_db, MedicalReport, ChatSession
from backend.services import chatbot_service

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])


class ChatRequest(BaseModel):
    report_id: int = Field(..., description="ID of the medical report providing context")
    message: str = Field(..., min_length=1, description="User message")
    session_id: Optional[int] = Field(None, description="Existing chat session ID (optional)")


@router.post("/chat", summary="Send a message to the chatbot")
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    # Load report for context
    report = db.query(MedicalReport).filter(MedicalReport.id == req.report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")

    context_text = report.extracted_text or report.summary_en or ""

    # Load or create a chat session
    session = None
    if req.session_id:
        session = db.query(ChatSession).filter(ChatSession.id == req.session_id).first()

    if session is None:
        session = ChatSession(report_id=req.report_id, messages=[])
        db.add(session)
        db.commit()
        db.refresh(session)

    history = list(session.messages or [])

    # Get bot response
    result = chatbot_service.chat(req.message, context_text=context_text, history=history)

    # Persist updated history
    session.messages = result["history"]
    session.updated_at = datetime.utcnow()
    db.commit()

    return {
        "session_id": session.id,
        "response": result["response"],
        "history": result["history"],
    }


@router.get("/start/{report_id}", summary="Get the opening chatbot message for a report")
def start_chat(report_id: int, db: Session = Depends(get_db)):
    report = db.query(MedicalReport).filter(MedicalReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")

    context_text = report.extracted_text or report.summary_en or ""
    greeting = chatbot_service.get_initial_greeting(context_text)

    # Create new session
    session = ChatSession(
        report_id=report_id,
        messages=[{"role": "assistant", "content": greeting}],
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return {
        "session_id": session.id,
        "response": greeting,
        "history": session.messages,
    }


@router.get("/session/{session_id}", summary="Get chat session history")
def get_session(session_id: int, db: Session = Depends(get_db)):
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    return {
        "session_id": session.id,
        "report_id": session.report_id,
        "messages": session.messages,
    }
