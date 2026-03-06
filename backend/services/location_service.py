"""
Location & Outbreak Monitoring Service.

Collects anonymised location data, detects symptom clusters, and generates
early outbreak alerts for diseases such as dengue, flu, etc.
"""

import logging
from collections import Counter
from datetime import datetime, timedelta
from typing import Any, Optional, List, Dict

logger = logging.getLogger(__name__)

# Minimum case count in a region to trigger an outbreak alert
OUTBREAK_THRESHOLD = 5

# Time window for outbreak detection (hours)
DETECTION_WINDOW_HOURS = 72

# Disease-to-symptom mapping for outbreak inference
DISEASE_SYMPTOM_MAP = {
    "dengue": {"fever", "rash", "joint pain", "headache", "eye pain", "vomiting"},
    "flu": {"fever", "cough", "fatigue", "body ache", "sore throat", "chills"},
    "covid": {"fever", "cough", "difficulty breathing", "loss of taste", "loss of smell", "fatigue"},
    "malaria": {"fever", "chills", "sweating", "headache", "vomiting", "muscle pain"},
    "cholera": {"diarrhoea", "vomiting", "dehydration", "muscle cramps"},
    "typhoid": {"fever", "abdominal pain", "headache", "diarrhoea", "fatigue"},
}


def infer_disease(symptoms: List[str]) -> Optional[str]:
    """
    Infer likely disease from a list of symptom strings.

    Returns the best-matching disease name or None.
    """
    symptom_set = {s.lower().strip() for s in symptoms}
    best_match = None
    best_score = 0

    for disease, disease_symptoms in DISEASE_SYMPTOM_MAP.items():
        overlap = len(symptom_set & disease_symptoms)
        if overlap > best_score:
            best_score = overlap
            best_match = disease

    return best_match if best_score >= 2 else None


def detect_outbreaks(db) -> List[Dict[str, Any]]:
    """
    Scan recent symptom logs and create / update outbreak alert records.

    Args:
        db: SQLAlchemy session.

    Returns:
        List of new or updated outbreak alert dicts.
    """
    from backend.models.database import SymptomLog, OutbreakAlert

    cutoff = datetime.utcnow() - timedelta(hours=DETECTION_WINDOW_HOURS)
    recent_logs = (
        db.query(SymptomLog)
        .filter(SymptomLog.reported_at >= cutoff)
        .all()
    )

    # Aggregate by region + inferred disease
    region_disease_counts: Dict[tuple, int] = Counter()
    for log in recent_logs:
        region = log.region or "Unknown"
        disease = infer_disease(log.symptoms or [])
        if disease:
            region_disease_counts[(region, disease)] += 1

    new_alerts = []
    for (region, disease), count in region_disease_counts.items():
        if count < OUTBREAK_THRESHOLD:
            continue

        # Check if an active alert already exists
        existing = (
            db.query(OutbreakAlert)
            .filter(
                OutbreakAlert.region == region,
                OutbreakAlert.disease == disease,
                OutbreakAlert.is_active == True,
            )
            .first()
        )

        severity = "Watch" if count < 10 else ("Warning" if count < 20 else "Emergency")
        message = (
            f"{count} cases of symptoms consistent with {disease} detected in "
            f"{region} within the last {DETECTION_WINDOW_HOURS} hours. "
            f"Please take precautions and consult a healthcare provider if you experience symptoms."
        )

        if existing:
            existing.case_count = count
            existing.severity = severity
            existing.message = message
            existing.updated_at = datetime.utcnow()
            db.commit()
            new_alerts.append(_alert_to_dict(existing))
        else:
            alert = OutbreakAlert(
                disease=disease,
                region=region,
                case_count=count,
                severity=severity,
                message=message,
            )
            db.add(alert)
            db.commit()
            db.refresh(alert)
            new_alerts.append(_alert_to_dict(alert))

    return new_alerts


def _alert_to_dict(alert) -> dict:
    return {
        "id": alert.id,
        "disease": alert.disease,
        "region": alert.region,
        "case_count": alert.case_count,
        "severity": alert.severity,
        "message": alert.message,
        "is_active": alert.is_active,
        "created_at": alert.created_at.isoformat() if alert.created_at else None,
    }


def get_active_alerts(db, region: Optional[str] = None) -> List[Dict[str, Any]]:
    """Return all active outbreak alerts, optionally filtered by region."""
    from backend.models.database import OutbreakAlert

    query = db.query(OutbreakAlert).filter(OutbreakAlert.is_active == True)
    if region:
        query = query.filter(OutbreakAlert.region.ilike(f"%{region}%"))
    return [_alert_to_dict(a) for a in query.all()]
