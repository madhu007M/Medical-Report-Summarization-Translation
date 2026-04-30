import re
from typing import Dict, List, Tuple


RISK_LEVELS = ["Low", "Moderate", "High"]


def _detect_bp(text: str) -> Tuple[int, int]:
    match = re.search(r"(\d{2,3})\s*/\s*(\d{2,3})", text)
    if not match:
        return 0, 0
    systolic, diastolic = int(match.group(1)), int(match.group(2))
    return systolic, diastolic


def _detect_temp(text: str) -> float:
    """Detect temperature value from text.

    Handles both 2-digit (98.6F) and 3-digit (103.5F, 100.2C) formats.
    Original regex r"(\d{2}\.d)" failed on 3-digit values like 103.5
    because \d{2} matched only the last 2 digits of the integer part,
    e.g. matching "03" in "103.5" giving 3.5 instead of 103.5.
    """
    match = re.search(r"(\d{2,3}\.\d+)\s*[CF]", text, flags=re.IGNORECASE)
    return float(match.group(1)) if match else 0.0


def evaluate_risk(report_text: str, symptoms: List[str]) -> Dict[str, object]:
    report_lower = report_text.lower()
    systolic, diastolic = _detect_bp(report_text)
    temperature = _detect_temp(report_text)

    alerts: List[str] = []
    risk_score = 0

    # ── Blood pressure ────────────────────────────────────────────────────────
    if systolic >= 180 or diastolic >= 120:
        alerts.append("Hypertensive crisis suspected; seek emergency care")
        risk_score += 6  # alone pushes to High (>= 6)
    elif systolic >= 140 or diastolic >= 90:
        alerts.append("Elevated blood pressure noted")
        risk_score += 2

    # ── Temperature ───────────────────────────────────────────────────────────
    if temperature >= 102:
        alerts.append("High fever detected")
        risk_score += 3  # alone gives Moderate (>= 3)
    elif temperature >= 100:
        alerts.append("Fever detected")
        risk_score += 1

    # ── User-reported symptoms ────────────────────────────────────────────────
    symptom_keywords = {
        "chest pain": 3,
        "shortness of breath": 3,
        "dizziness": 2,
        "vomiting": 1,
        "bleeding": 3,
        "weakness": 1,
        "rash": 1,
        "fever": 1,
    }

    for symptom in symptoms:
        weight = symptom_keywords.get(symptom.lower(), 0)
        risk_score += weight
        if weight >= 2:
            alerts.append(f"Symptom reported: {symptom}")

    # ── Critical clinical terms — checked separately so both score ────────────
    if "sepsis" in report_lower:
        alerts.append("Critical term detected in report: sepsis")
        risk_score += 3
    if "shock" in report_lower:
        alerts.append("Critical term detected in report: shock")
        risk_score += 3

    # ── Risk classification ───────────────────────────────────────────────────
    if risk_score >= 6:
        level = "High"
        recommendation = "Go to the nearest hospital or call emergency services immediately."
    elif risk_score >= 3:
        level = "Moderate"
        recommendation = "Schedule an urgent visit with a doctor and monitor symptoms closely."
    else:
        level = "Low"
        recommendation = "Maintain hydration, rest, and follow up with routine care if symptoms persist."

    return {
        "risk_level": level,
        "risk_score": risk_score,
        "alerts": alerts,
        "recommendation": recommendation,
    }

