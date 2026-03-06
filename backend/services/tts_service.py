"""
Text-to-Speech Service — converts text summaries to audio using gTTS.

Generates MP3 files saved to the configured AUDIO_DIR.
"""

import hashlib
import logging
from pathlib import Path
from typing import Optional

from backend.config import AUDIO_DIR

logger = logging.getLogger(__name__)

# gTTS language codes
_GTTS_LANG_MAP = {
    "en": "en",
    "hi": "hi",
    "kn": "kn",
    "ta": "ta",
}


def _sanitize_for_filename(text: str, max_len: int = 20) -> str:
    """Return a short slug derived from *text* for use in file names."""
    slug = "".join(c if c.isalnum() else "_" for c in text[:max_len])
    return slug.strip("_") or "audio"


def generate_audio(text: str, lang: str = "en", report_id: Optional[int] = None) -> Optional[str]:
    """
    Convert *text* to speech and save as an MP3 file.

    Args:
        text:      The text to speak.
        lang:      Language code ('en', 'hi', 'kn', 'ta').
        report_id: Optional report ID used in the filename for traceability.

    Returns:
        Relative path to the generated MP3 file, or None on failure.
    """
    if not text or not text.strip():
        logger.warning("Empty text passed to generate_audio.")
        return None

    gtts_lang = _GTTS_LANG_MAP.get(lang, "en")

    # Build a deterministic filename so the same content isn't re-generated
    content_hash = hashlib.md5(text.encode()).hexdigest()[:8]
    prefix = f"report_{report_id}_" if report_id else ""
    filename = f"{prefix}{lang}_{content_hash}.mp3"
    output_path = AUDIO_DIR / filename

    if output_path.exists():
        logger.info("Audio cache hit: %s", filename)
        return str(output_path)

    try:
        from gtts import gTTS

        tts = gTTS(text=text, lang=gtts_lang, slow=False)
        tts.save(str(output_path))
        logger.info("Audio generated: %s", filename)
        return str(output_path)
    except Exception as exc:
        logger.error("gTTS failed for lang '%s': %s", lang, exc)
        return None


def generate_all_audio(
    summaries: dict, report_id: Optional[int] = None
) -> dict:
    """
    Generate audio for each language in *summaries*.

    Args:
        summaries: dict like {'en': '...', 'hi': '...', 'kn': '...', 'ta': '...'}
        report_id: Optional report ID for filenames.

    Returns:
        dict like {'en': '/path/to/en.mp3', 'hi': None, ...}
    """
    return {
        lang: generate_audio(text, lang=lang, report_id=report_id)
        for lang, text in summaries.items()
        if text
    }
