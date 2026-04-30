from typing import Dict, List

from sqlalchemy.orm import Session

from ..models import DoctorAlert


def create_alert(db: Session, doctor_name: str, region: str, title: str, message: str) -> DoctorAlert:
    alert = DoctorAlert(doctor_name=doctor_name, region=region, title=title, message=message)
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


def list_alerts(db: Session, region: str = "") -> List[Dict[str, str]]:
    query = db.query(DoctorAlert)
    if region:
        query = query.filter(DoctorAlert.region.ilike(f"%{region}%"))
    alerts = query.order_by(DoctorAlert.created_at.desc()).all()
    return [
        {
            "doctor": alert.doctor_name,
            "region": alert.region,
            "title": alert.title,
            "message": alert.message,
            "created_at": alert.created_at.isoformat(),
        }
        for alert in alerts
    ]
