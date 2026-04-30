from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import Dict, List

from sqlalchemy.orm import Session

from ..config import get_settings
from ..models import OutbreakCluster, SymptomLog

settings = get_settings()


def record_symptoms(db: Session, report_id: int, symptoms: List[str], location: str) -> None:
    for symptom in symptoms:
        log = SymptomLog(report_id=report_id, symptom=symptom, location=location)
        db.add(log)
    db.commit()


def detect_clusters(db: Session, lookback_hours: int = 72) -> List[Dict[str, object]]:
    cutoff = datetime.utcnow() - timedelta(hours=lookback_hours)
    recent = db.query(SymptomLog).filter(SymptomLog.created_at >= cutoff).all()

    buckets: Dict[str, Counter] = defaultdict(Counter)
    for log in recent:
        loc = log.location or "unknown"
        buckets[loc][log.symptom.lower()] += 1

    clusters: List[Dict[str, object]] = []
    for location, counter in buckets.items():
        total = sum(counter.values())
        if total >= settings.outbreak_threshold:
            top_symptom, count = counter.most_common(1)[0]
            risk_score = min(1.0, total / (settings.outbreak_threshold * 2))
            cluster = OutbreakCluster(
                disease=top_symptom,
                location=location,
                case_count=total,
                risk_score=risk_score,
                last_detected_at=datetime.utcnow(),
            )
            db.add(cluster)
            db.commit()
            clusters.append(
                {
                    "location": location,
                    "suspected_cause": top_symptom,
                    "cases": total,
                    "risk_score": risk_score,
                }
            )
    return clusters
