"""
Risk Analysis API — analyse text and symptoms for medical risk.
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional

from backend.services import risk_service

router = APIRouter(prefix="/risk", tags=["Risk Analysis"])


class RiskRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Extracted medical report text")
    symptoms: Optional[list[str]] = Field(default=None, description="List of reported symptoms")


@router.post("/analyse", summary="Analyse medical text and symptoms for risk level")
def analyse_risk(req: RiskRequest):
    result = risk_service.analyse_risk(req.text, req.symptoms or [])
    return {
        "risk_level": result["risk_level"],
        "risk_score": result["risk_score"],
        "details": result["details"],
        "recommendations": result["recommendations"],
    }
