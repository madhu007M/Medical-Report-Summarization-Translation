"""Text-to-Speech Module — Voice-based Medical Report Explanation.

Supports all 7 translation languages with high-quality pronunciation of
medical terms through preprocessing and abbreviation expansion.

Key features:
- Medical abbreviation expansion (BP → blood pressure, etc.)
- Text chunking for long reports (gTTS has character limits)
- Speed control (slow mode for better comprehension)
- Language-specific voice optimization
"""
import io
import logging
import re
import uuid
from pathlib import Path
from typing import Dict, List, Optional

from gtts import gTTS

logger = logging.getLogger(__name__)
AUDIO_DIR = Path(__file__).resolve().parent.parent / "static" / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

# Maximum characters per gTTS call (conservative limit to avoid failures)
_GTTS_MAX_CHARS = 3000

# Medical abbreviations that should be expanded for better TTS pronunciation
_MEDICAL_ABBREVIATIONS: Dict[str, str] = {
    r'\bBP\b': 'blood pressure',
    r'\bHR\b': 'heart rate',
    r'\bRR\b': 'respiratory rate',
    r'\bTemp\b': 'temperature',
    r'\bWBC\b': 'white blood cell',
    r'\bRBC\b': 'red blood cell',
    r'\bHb\b': 'hemoglobin',
    r'\bHgb\b': 'hemoglobin',
    r'\bO2\b': 'oxygen',
    r'\bCO2\b': 'carbon dioxide',
    r'\bECG\b': 'electrocardiogram',
    r'\bEKG\b': 'electrocardiogram',
    r'\bCT\b': 'C T scan',
    r'\bMRI\b': 'M R I',
    r'\bDr\b\.': 'Doctor',
    r'\bMr\b\.': 'Mister',
    r'\bMrs\b\.': 'Misses',
    r'\bLab\b': 'laboratory',
    r'\bMg\b': 'milligrams',
    r'\bMl\b': 'milliliters',
    r'\bIV\b': 'intravenous',
    r'\bPO\b': 'by mouth',
    r'\bBID\b': 'twice daily',
    r'\bTID\b': 'three times daily',
    r'\bQID\b': 'four times daily',
}

# Language code to gTTS TLD mapping for better voice quality
# Different regional TLDs have better voices for certain languages
_LANGUAGE_TLD_MAP: Dict[str, str] = {
    "en": "com",        # US English (clear)
    "hi": "co.in",      # Indian Hindi
    "kn": "co.in",      # Indian Kannada
    "ta": "co.in",      # Indian Tamil
    "te": "co.in",      # Indian Telugu
    "mr": "co.in",      # Indian Marathi
    "bn": "com.bd",     # Bangladeshi Bengali
}


def _expand_medical_abbreviations(text: str) -> str:
    """Expand common medical abbreviations for better TTS pronunciation.

    Example: "BP: 120/80" → "blood pressure: 120 over 80"
    """
    result = text
    for pattern, replacement in _MEDICAL_ABBREVIATIONS.items():
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

    # Special formatting: slash in BP readings
    result = re.sub(r'(\d{2,3})\s*/\s*(\d{2,3})', r'\1 over \2', result)

    return result


def _clean_for_speech(text: str) -> str:
    """Clean text to improve TTS pronunciation quality.

    - Removes URLs (sound terrible when read aloud)
    - Normalizes whitespace
    - Expands medical abbreviations
    """
    # Remove URLs
    text = re.sub(r'http[s]?://\S+', 'link removed', text)

    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)

    # Expand medical abbreviations
    text = _expand_medical_abbreviations(text)

    return text.strip()


def _chunk_text_for_tts(text: str, max_chars: int = _GTTS_MAX_CHARS) -> List[str]:
    """Split text into chunks that gTTS can handle.

    Splits at sentence boundaries when possible to avoid mid-sentence cuts.
    """
    if len(text) <= max_chars:
        return [text]

    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks: List[str] = []
    current = ""

    for sentence in sentences:
        if not current:
            current = sentence
        elif len(current) + 1 + len(sentence) <= max_chars:
            current += " " + sentence
        else:
            chunks.append(current)
            current = sentence

    if current:
        chunks.append(current)

    return chunks if chunks else [text]


def synthesize_audio_bytes(text: str, language: str = "en", slow: bool = False) -> bytes:
    """Generate audio bytes (MP3) from text using gTTS.

    Args:
        text: Text to convert to speech
        language: Language code (en, hi, kn, ta, te, mr, bn)
        slow: If True, use slower speech rate for better comprehension

    Returns:
        MP3 audio bytes, or empty bytes on error

    The text is preprocessed to expand medical abbreviations and chunk
    long content into multiple gTTS calls which are then concatenated.
    """
    if not text or not text.strip():
        logger.warning("Empty text provided to TTS")
        return b""

    try:
        # Clean and preprocess text
        cleaned_text = _clean_for_speech(text)
        chunks = _chunk_text_for_tts(cleaned_text)

        # Get optimal TLD for this language
        tld = _LANGUAGE_TLD_MAP.get(language, "com")

        # Generate audio for each chunk
        audio_parts: List[bytes] = []
        for chunk in chunks:
            tts = gTTS(text=chunk, lang=language, tld=tld, slow=slow)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            audio_parts.append(fp.getvalue())

        # Concatenate all chunks (MP3 allows simple byte concatenation)
        return b"".join(audio_parts)

    except Exception as exc:
        logger.exception("TTS synthesis failed for language '%s': %s", language, exc)
        return b""


def synthesize_audio(text: str, language: str = "en", slow: bool = False) -> str:
    """Generate an MP3 file and return its path.

    Deprecated: prefer synthesize_audio_bytes for streaming use cases.
    Kept for backward compatibility.
    """
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    file_id = uuid.uuid4().hex
    output_path = AUDIO_DIR / f"explanation_{file_id}.mp3"

    try:
        audio_bytes = synthesize_audio_bytes(text, language, slow)
        if audio_bytes:
            output_path.write_bytes(audio_bytes)
            return str(output_path)
    except Exception as exc:
        logger.exception("TTS file generation failed: %s", exc)

    return ""


def synthesize_sentences(text: str, language: str = "en", slow: bool = False) -> List[Dict[str, object]]:
    """Generate audio for each sentence individually.

    Returns a list of dicts with sentence text and audio bytes.
    Useful for sentence-by-sentence playback in interactive UIs.
    """
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    results: List[Dict[str, object]] = []

    for i, sentence in enumerate(sentences):
        if not sentence.strip():
            continue

        audio_bytes = synthesize_audio_bytes(sentence, language, slow)
        results.append({
            "index": i,
            "text": sentence,
            "audio_bytes": audio_bytes,
            "char_count": len(sentence),
        })

    return results
