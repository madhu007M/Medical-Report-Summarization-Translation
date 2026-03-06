"""
Summarization Service — generates a patient-friendly summary from medical text.

Uses a HuggingFace summarization pipeline.  Falls back gracefully when the
model cannot be loaded (e.g., in environments without internet access).
"""

import logging
import re
from functools import lru_cache
from typing import Optional

logger = logging.getLogger(__name__)

# Maximum tokens the model can handle in one pass
_MAX_INPUT_TOKENS = 1024


@lru_cache(maxsize=1)
def _get_pipeline():
    """Load the summarization pipeline once and cache it."""
    try:
        from transformers import pipeline
        from backend.config import SUMMARIZATION_MODEL

        logger.info("Loading summarization model: %s", SUMMARIZATION_MODEL)
        pipe = pipeline(
            "summarization",
            model=SUMMARIZATION_MODEL,
            tokenizer=SUMMARIZATION_MODEL,
        )
        logger.info("Summarization model loaded.")
        return pipe
    except Exception as exc:
        logger.warning("Could not load summarization model: %s", exc)
        return None


def _truncate_text(text: str, max_words: int = 700) -> str:
    """Truncate text to roughly max_words words to stay within model limits."""
    words = text.split()
    return " ".join(words[:max_words]) if len(words) > max_words else text


def _rule_based_summary(text: str) -> str:
    """
    Very lightweight rule-based summary used when the AI model is unavailable.
    Extracts key sentences containing medical keywords.
    """
    keywords = [
        "diagnosis", "result", "impression", "finding", "recommend",
        "prescribed", "treatment", "glucose", "hemoglobin", "blood pressure",
        "normal", "abnormal", "elevated", "low", "high", "severe", "moderate",
    ]
    sentences = re.split(r"(?<=[.!?])\s+", text)
    key_sentences = [
        s.strip() for s in sentences
        if any(kw in s.lower() for kw in keywords)
    ][:6]
    if key_sentences:
        return " ".join(key_sentences)
    # Last resort: return first 3 sentences
    return " ".join(sentences[:3])


def _make_patient_prompt(text: str) -> str:
    """Prepend a prompt prefix to guide the model toward plain-language output."""
    prefix = (
        "Summarize the following medical report in simple, easy-to-understand "
        "language for a patient with no medical background. "
        "Highlight key findings, diagnoses, and any recommended actions:\n\n"
    )
    return prefix + text


def summarize(text: str) -> str:
    """
    Generate a patient-friendly summary of the provided medical text.

    Returns the summary string.
    """
    if not text or not text.strip():
        return "No text provided for summarization."

    truncated = _truncate_text(text)
    pipe = _get_pipeline()

    if pipe is None:
        logger.warning("Using rule-based fallback summary.")
        return _rule_based_summary(truncated)

    try:
        prompt = _make_patient_prompt(truncated)
        result = pipe(
            prompt,
            max_length=300,
            min_length=80,
            do_sample=False,
            truncation=True,
        )
        return result[0]["summary_text"].strip()
    except Exception as exc:
        logger.error("Summarization pipeline error: %s", exc)
        return _rule_based_summary(truncated)
