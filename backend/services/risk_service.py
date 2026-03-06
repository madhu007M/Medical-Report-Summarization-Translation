"""
Medical Risk Detection Service.

Analyses extracted medical text and optional symptom lists against rule-based
thresholds to produce a risk level (Low / Moderate / High) and urgency score.
"""

import re
import logging
from typing import Any, Optional

from backend.config import RISK_THRESHOLDS

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_value(text: str, pattern: str) -> float | None:
    """Extract the first numeric value matched by *pattern* from *text*."""
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        try:
            return float(match.group(1).replace(",", ""))
        except ValueError:
            pass
    return None


def _check_glucose(text: str) -> dict:
    thresholds = RISK_THRESHOLDS["glucose"]
    value = _extract_value(
        text,
        r"(?:fasting\s+)?(?:blood\s+)?glucose[:\s]+([0-9]+(?:\.[0-9]+)?)"
    )
    if value is None:
        return {}
    if value >= thresholds["high_severe"]:
        return {"glucose": {"value": value, "level": "High", "score": 3,
                             "note": f"Glucose {value} mg/dL — severely elevated. Seek immediate care."}}
    if value >= thresholds["high_moderate"]:
        return {"glucose": {"value": value, "level": "Moderate", "score": 2,
                             "note": f"Glucose {value} mg/dL — elevated. Consult your doctor."}}
    if value < thresholds["low"]:
        return {"glucose": {"value": value, "level": "Moderate", "score": 2,
                             "note": f"Glucose {value} mg/dL — low (hypoglycemia). Eat something sweet and consult a doctor."}}
    return {"glucose": {"value": value, "level": "Low", "score": 1,
                         "note": f"Glucose {value} mg/dL — within normal range."}}


def _check_hemoglobin(text: str) -> dict:
    thresholds = RISK_THRESHOLDS["hemoglobin"]
    value = _extract_value(text, r"h(?:ae|e)moglobin[:\s]+([0-9]+(?:\.[0-9]+)?)")
    if value is None:
        return {}
    if value <= thresholds["low_severe"]:
        return {"hemoglobin": {"value": value, "level": "High", "score": 3,
                                "note": f"Haemoglobin {value} g/dL — severe anaemia. Urgent care needed."}}
    if value <= thresholds["low_moderate"]:
        return {"hemoglobin": {"value": value, "level": "Moderate", "score": 2,
                                "note": f"Haemoglobin {value} g/dL — moderate anaemia. Consult a doctor."}}
    return {"hemoglobin": {"value": value, "level": "Low", "score": 1,
                            "note": f"Haemoglobin {value} g/dL — normal."}}


def _check_wbc(text: str) -> dict:
    thresholds = RISK_THRESHOLDS["wbc"]
    value = _extract_value(text, r"(?:wbc|white\s+blood\s+cell)[:\s]+([0-9]+(?:\.[0-9]+)?)")
    if value is None:
        return {}
    if value >= thresholds["high_severe"]:
        return {"wbc": {"value": value, "level": "High", "score": 3,
                         "note": f"WBC {value} K/uL — very high; possible infection or serious condition."}}
    if value >= thresholds["high_moderate"]:
        return {"wbc": {"value": value, "level": "Moderate", "score": 2,
                         "note": f"WBC {value} K/uL — mildly elevated; monitor for infection."}}
    if value < thresholds["low"]:
        return {"wbc": {"value": value, "level": "Moderate", "score": 2,
                         "note": f"WBC {value} K/uL — low; consult your doctor."}}
    return {"wbc": {"value": value, "level": "Low", "score": 1,
                     "note": f"WBC {value} K/uL — normal."}}


def _check_bp(text: str) -> dict:
    thresholds_s = RISK_THRESHOLDS["bp_systolic"]
    thresholds_d = RISK_THRESHOLDS["bp_diastolic"]
    match = re.search(r"b(?:lood\s+)?p(?:ressure)?[:\s]+([0-9]+)\s*/\s*([0-9]+)", text, re.IGNORECASE)
    if not match:
        return {}
    systolic, diastolic = float(match.group(1)), float(match.group(2))
    if systolic >= thresholds_s["high_severe"] or diastolic >= thresholds_d["high_severe"]:
        return {"bp": {"value": f"{systolic}/{diastolic}", "level": "High", "score": 3,
                        "note": f"BP {systolic}/{diastolic} mmHg — hypertensive crisis. Seek emergency care."}}
    if systolic >= thresholds_s["high_moderate"] or diastolic >= thresholds_d["high_moderate"]:
        return {"bp": {"value": f"{systolic}/{diastolic}", "level": "Moderate", "score": 2,
                        "note": f"BP {systolic}/{diastolic} mmHg — stage 1 hypertension. Monitor regularly."}}
    if systolic < thresholds_s["low"] or diastolic < thresholds_d["low"]:
        return {"bp": {"value": f"{systolic}/{diastolic}", "level": "Moderate", "score": 2,
                        "note": f"BP {systolic}/{diastolic} mmHg — low; ensure adequate hydration."}}
    return {"bp": {"value": f"{systolic}/{diastolic}", "level": "Low", "score": 1,
                    "note": f"BP {systolic}/{diastolic} mmHg — normal."}}


def _check_temperature(text: str) -> dict:
    thresholds = RISK_THRESHOLDS["temperature"]
    value = _extract_value(text, r"temp(?:erature)?[:\s]+([0-9]+(?:\.[0-9]+)?)")
    if value is None:
        return {}
    if value >= thresholds["high_severe"]:
        return {"temperature": {"value": value, "level": "High", "score": 3,
                                 "note": f"Temperature {value}°F — high fever. Seek immediate medical attention."}}
    if value >= thresholds["high_moderate"]:
        return {"temperature": {"value": value, "level": "Moderate", "score": 2,
                                 "note": f"Temperature {value}°F — fever present. Rest and monitor closely."}}
    if value < thresholds["low"]:
        return {"temperature": {"value": value, "level": "Moderate", "score": 2,
                                 "note": f"Temperature {value}°F — hypothermia. Seek medical attention."}}
    return {"temperature": {"value": value, "level": "Low", "score": 1,
                             "note": f"Temperature {value}°F — normal."}}


def _check_spo2(text: str) -> dict:
    thresholds = RISK_THRESHOLDS["spo2"]
    value = _extract_value(text, r"sp[o0]2[:\s]+([0-9]+(?:\.[0-9]+)?)")
    if value is None:
        return {}
    if value <= thresholds["low_severe"]:
        return {"spo2": {"value": value, "level": "High", "score": 3,
                          "note": f"SpO2 {value}% — critically low. Emergency oxygen needed."}}
    if value <= thresholds["low_moderate"]:
        return {"spo2": {"value": value, "level": "Moderate", "score": 2,
                          "note": f"SpO2 {value}% — low oxygen saturation. Consult doctor immediately."}}
    return {"spo2": {"value": value, "level": "Low", "score": 1,
                      "note": f"SpO2 {value}% — normal."}}


def _symptom_score(symptoms: list) -> dict:
    """Map reported symptoms to a risk contribution."""
    HIGH_RISK_SYMPTOMS = {
        "chest pain", "difficulty breathing", "shortness of breath",
        "unconscious", "severe headache", "sudden weakness", "high fever",
        "coughing blood", "vomiting blood",
    }
    MODERATE_RISK_SYMPTOMS = {
        "fever", "persistent cough", "vomiting", "diarrhoea", "diarrhea",
        "dizziness", "fatigue", "swelling", "rash", "joint pain",
    }
    score = 0
    notes = []
    for sym in symptoms:
        sym_lower = sym.lower().strip()
        if sym_lower in HIGH_RISK_SYMPTOMS:
            score += 3
            notes.append(f"High-risk symptom: {sym}")
        elif sym_lower in MODERATE_RISK_SYMPTOMS:
            score += 2
            notes.append(f"Moderate-risk symptom: {sym}")
        else:
            score += 1
    return {"symptom_score": score, "symptom_notes": notes}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def analyse_risk(extracted_text: str, symptoms: Optional[list] = None) -> dict:
    """
    Analyse *extracted_text* and optional *symptoms* list.

    Returns:
        {
            "risk_level": "Low" | "Moderate" | "High",
            "risk_score": float,
            "details": { ... per-parameter results ... },
            "recommendations": [ ... action strings ... ],
        }
    """
    text = extracted_text or ""
    symptoms = symptoms or []

    # Run all checks
    details: dict = {}
    details.update(_check_glucose(text))
    details.update(_check_hemoglobin(text))
    details.update(_check_wbc(text))
    details.update(_check_bp(text))
    details.update(_check_temperature(text))
    details.update(_check_spo2(text))

    # Symptom contribution
    sym_result = _symptom_score(symptoms)
    sym_score = sym_result["symptom_score"]

    # Aggregate score from vitals
    vitals_score = sum(v.get("score", 0) for v in details.values() if isinstance(v, dict))
    total_score = vitals_score + sym_score

    # Determine level
    high_count = sum(1 for v in details.values() if isinstance(v, dict) and v.get("level") == "High")
    moderate_count = sum(1 for v in details.values() if isinstance(v, dict) and v.get("level") == "Moderate")

    if high_count >= 1 or total_score >= 6:
        risk_level = "High"
    elif moderate_count >= 2 or total_score >= 4:
        risk_level = "Moderate"
    else:
        risk_level = "Low"

    # Build recommendations
    recommendations = []
    if risk_level == "High":
        recommendations.append("⚠️ Visit the nearest emergency hospital immediately.")
        recommendations.append("Do not drive yourself — ask for assistance.")
    elif risk_level == "Moderate":
        recommendations.append("📋 Schedule an appointment with your doctor within 1–2 days.")
        recommendations.append("Monitor your symptoms and rest.")
    else:
        recommendations.append("✅ Values appear within acceptable ranges.")
        recommendations.append("Maintain a healthy lifestyle and attend routine check-ups.")

    if sym_result["symptom_notes"]:
        recommendations.extend(sym_result["symptom_notes"])

    return {
        "risk_level": risk_level,
        "risk_score": float(total_score),
        "details": details,
        "recommendations": recommendations,
    }
