"""
Location & Outbreak Alerts API.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Optional

from backend.models.database import get_db, SymptomLog, OutbreakAlert
from backend.services import location_service

router = APIRouter(prefix="/alerts", tags=["Outbreak Alerts"])


class SymptomLogRequest(BaseModel):
    symptoms: list[str] = Field(..., description="List of reported symptoms")
    user_id: Optional[int] = None
    location_lat: Optional[float] = None
    location_lon: Optional[float] = None
    region: Optional[str] = None


@router.post("/log-symptoms", summary="Log user symptoms for outbreak monitoring")
def log_symptoms(req: SymptomLogRequest, db: Session = Depends(get_db)):
    log = SymptomLog(
        user_id=req.user_id,
        symptoms=req.symptoms,
        location_lat=req.location_lat,
        location_lon=req.location_lon,
        region=req.region,
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    # Infer disease
    inferred = location_service.infer_disease(req.symptoms)

    # Trigger outbreak detection
    new_alerts = location_service.detect_outbreaks(db)

    return {
        "log_id": log.id,
        "inferred_disease": inferred,
        "new_alerts_generated": len(new_alerts),
        "alerts": new_alerts,
    }


@router.get("/active", summary="Get active outbreak alerts")
def get_active_alerts(region: Optional[str] = None, db: Session = Depends(get_db)):
    alerts = location_service.get_active_alerts(db, region=region)
    return {"alerts": alerts, "total": len(alerts)}


@router.get("/detect", summary="Run outbreak detection scan manually")
def run_detection(db: Session = Depends(get_db)):
    alerts = location_service.detect_outbreaks(db)
    return {"alerts_generated_or_updated": alerts, "count": len(alerts)}


@router.put("/{alert_id}/deactivate", summary="Deactivate an outbreak alert")
def deactivate_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(OutbreakAlert).filter(OutbreakAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found.")
    alert.is_active = False
    db.commit()
    return {"message": f"Alert {alert_id} deactivated."}
