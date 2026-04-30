import logging
import re
from functools import lru_cache
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# Medical term -> plain language replacements (used in smart extractor)
# --------------------------------------------------------------------------- #
_MEDICAL_TERMS: Dict[str, str] = {
    r"\bhypertension\b": "high blood pressure",
    r"\bhypotension\b": "low blood pressure",
    r"\bdyspnea\b": "difficulty in breathing",
    r"\btachycardia\b": "fast heartbeat",
    r"\bbradycardia\b": "slow heartbeat",
    r"\bpyrexia\b": "fever",
    r"\bmyalgia\b": "muscle pain",
    r"\bgastroenteritis\b": "stomach infection",
    r"\bpneumonia\b": "lung infection",
    r"\bdiabetes\s+mellitus\b": "diabetes (high blood sugar)",
    r"\bdiabetes\b": "diabetes (high blood sugar)",
    r"\bhyperglycemia\b": "very high blood sugar",
    r"\banemia\b": "low blood / anemia",
    r"\bmalaria\b": "malaria (mosquito fever)",
    r"\bdengue\b": "dengue fever",
    r"\bchikungunya\b": "chikungunya fever",
    r"\btyphoid\b": "typhoid fever",
    r"\bjaundice\b": "jaundice (yellow eyes/skin)",
    r"\bdiarrhea\b": "loose motions / diarrhea",
    r"\bfatigue\b": "feeling very tired and weak",
    r"\bchills\b": "shivering / chills",
    r"\bnausea\b": "feeling like vomiting",
    r"\bpalpitations\b": "feeling heartbeat too strongly",
    r"\binsomnia\b": "unable to sleep",
}


def _apply_plain_terms(text: str) -> str:
    for pattern, replacement in _MEDICAL_TERMS.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text


def _smart_extract_summary(text: str) -> str:
    """Extract key clinical facts and present them in plain, simple language.

    Designed for rural / non-medical users who need clear, jargon-free output.
    Works entirely without ML models so it always succeeds.
    """
    if not text or not text.strip():
        return "No health report information was provided."

    cleaned = re.sub(r"\s+", " ", text.strip())
    lower = cleaned.lower()
    lines = []

    # ── Patient info ─────────────────────────────────────────────────────── #
    name_m = re.search(
        r"(?:patient\s+name|patient)\s*[:/\-]?\s*([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+)",
        cleaned, re.IGNORECASE,
    )
    age_m = re.search(
        r"(?:age(?:\s*/\s*sex)?)\s*[:/\-]?\s*(\d{1,3})\s*(?:/\s*(male|female|m|f)\b)?",
        cleaned, re.IGNORECASE,
    )
    if name_m or age_m:
        parts = []
        if name_m:
            parts.append(name_m.group(1).strip())
        if age_m:
            parts.append(f"Age {age_m.group(1)}")
            if age_m.group(2):
                parts.append(age_m.group(2).capitalize())
        lines.append("👤 Patient: " + ", ".join(parts))

    # ── Chief complaint ───────────────────────────────────────────────────── #
    cc_m = re.search(
        r"(?:chief\s+complaint|main\s+complaint|presenting\s+(?:with|complaint))\s*[:/\-]?\s*(.+?)(?:\.|history|\n|$)",
        cleaned, re.IGNORECASE,
    )
    if cc_m:
        complaint = _apply_plain_terms(cc_m.group(1).strip().rstrip("."))
        lines.append(f"🤒 Main Problem: {complaint}")

    # ── Temperature ───────────────────────────────────────────────────────── #
    temp_m = re.search(r"(\d{2,3}(?:\.\d)?)\s*[°º]?\s*([FC])\b", cleaned)
    if temp_m:
        val = float(temp_m.group(1))
        unit = temp_m.group(2).upper()
        val_f = val if unit == "F" else (val * 9 / 5 + 32)
        if val_f >= 103:
            tip = "⚠️ Very high fever — needs urgent care"
        elif val_f >= 101:
            tip = "⚠️ High fever — see a doctor soon"
        elif val_f >= 99.1:
            tip = "Mild fever — rest and drink fluids"
        else:
            tip = "Normal"
        lines.append(f"🌡️ Temperature: {val}°{unit} — {tip}")

    # ── Blood pressure ────────────────────────────────────────────────────── #
    bp_m = re.search(
        r"(?:BP|blood\s+pressure)\s*[:\-]?\s*(\d{2,3})\s*/\s*(\d{2,3})",
        cleaned, re.IGNORECASE,
    )
    if bp_m:
        s, d = int(bp_m.group(1)), int(bp_m.group(2))
        if s >= 180 or d >= 120:
            note = "⚠️ Dangerously high — see doctor immediately"
        elif s >= 140 or d >= 90:
            note = "⚠️ High blood pressure — needs treatment"
        elif s >= 130 or d >= 80:
            note = "Slightly high — please monitor"
        elif s < 90 or d < 60:
            note = "⚠️ Low — rest and drink water"
        else:
            note = "Normal"
        lines.append(f"💓 Blood Pressure: {s}/{d} mmHg — {note}")

    # ── Symptoms ──────────────────────────────────────────────────────────── #
    symptom_map = {
        "fever": "fever", "cough": "cough", "headache": "headache",
        "fatigue": "tiredness / weakness", "nausea": "feeling like vomiting",
        "vomiting": "vomiting", "diarrhea": "loose motions",
        "chills": "chills / shivering", "chest pain": "chest pain",
        "body ache": "body pain", "weakness": "weakness",
        "dizziness": "dizziness", "rash": "skin rash",
        "shortness of breath": "difficulty breathing",
        "sore throat": "sore throat", "runny nose": "runny nose",
        "muscle pain": "muscle pain", "joint pain": "joint pain",
        "abdominal pain": "stomach pain", "back pain": "back pain",
    }
    found = [label for kw, label in symptom_map.items() if kw in lower]
    if found:
        lines.append(f"🔍 Symptoms: {', '.join(found[:7])}")

    # ── Diagnosis / assessment ────────────────────────────────────────────── #
    diag_m = re.search(
        r"(?:assessment|diagnosis|impression|conclusion|plan)\s*[:/\-]?\s*(.+?)(?:\n|$)",
        cleaned, re.IGNORECASE,
    )
    if diag_m:
        diag = _apply_plain_terms(diag_m.group(1).strip())
        lines.append(f"🩺 Doctor's Finding: {diag[:180]}")

    # ── Medications ───────────────────────────────────────────────────────── #
    med_m = re.search(
        r"(?:prescribed|medications?|treatment|medicine)\s*[:/\-]?\s*([A-Z][a-zA-Z0-9\s,\-]+(?:\s*\d+\s*mg)?)",
        cleaned,
    )
    if med_m:
        lines.append(f"💊 Medicines: {med_m.group(1).strip()[:140]}")

    # ── Follow-up ─────────────────────────────────────────────────────────── #
    fu_m = re.search(
        r"(?:follow[- ]?up|review|next\s+visit)\s*[:/\-]?\s*(.+?)(?:\n|$)",
        cleaned, re.IGNORECASE,
    )
    if fu_m:
        lines.append(f"📅 Next Visit: {fu_m.group(1).strip()[:100]}")

    if not lines:
        # No structured data: apply plain-term replacements and return first sentences
        simple = _apply_plain_terms(cleaned)
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", simple) if len(s.strip()) > 15]
        lines = sentences[:3] if sentences else [simple[:350]]

    header = "📋 Simple Health Report Summary:\n"
    return header + "\n".join(lines)


@lru_cache(maxsize=1)
def _get_summarizer(model_name: str):
    """Load BART-based summarizer using direct model loading (avoids broken pipeline task registry)."""
    logger.info("Loading summarization model: %s", model_name)
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM  # noqa: PLC0415
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    return tokenizer, model


def simplify_report(text: str, model_name: str) -> Dict[str, str]:
    """Summarize clinical text into a patient-friendly plain-language paragraph.

    Primary path: BART via AutoModelForSeq2SeqLM (bypasses broken pipeline registry).
    Fallback: rule-based smart extractor that always returns useful output.
    """
    try:
        tokenizer, model = _get_summarizer(model_name)
        inputs = tokenizer(
            text, return_tensors="pt", max_length=1024, truncation=True
        )
        summary_ids = model.generate(
            inputs["input_ids"],
            max_length=180,
            min_length=40,
            num_beams=4,
            length_penalty=2.0,
            early_stopping=True,
        )
        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        return {"summary": summary}
    except Exception as exc:
        logger.exception("Summarization model failed, using smart extractor: %s", exc)
        return {"summary": _smart_extract_summary(text)}
