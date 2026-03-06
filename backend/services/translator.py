"""
Translation Service — translates text between English and Indian languages.

Supported target languages: hi (Hindi), kn (Kannada), ta (Tamil).

Strategy:
1. Try MarianMT via HuggingFace Transformers (Helsinki-NLP opus-mt models).
2. Fall back to googletrans (unofficial Google Translate) if available.
3. Return original text with a note if all else fails.
"""

import logging
from functools import lru_cache
from typing import Optional

logger = logging.getLogger(__name__)

# MarianMT model IDs for supported language pairs
_MARIAN_MODELS = {
    "hi": "Helsinki-NLP/opus-mt-en-hi",
    "kn": "Helsinki-NLP/opus-mt-en-mul",  # multilingual, supports Kannada
    "ta": "Helsinki-NLP/opus-mt-en-mul",  # multilingual, supports Tamil
}

# Language codes for the multilingual model (>>lang<<)
_MARIAN_LANG_TAGS = {
    "kn": ">>kan<<",
    "ta": ">>tam<<",
}


@lru_cache(maxsize=8)
def _get_marian_pipeline(lang_code: str):
    """Load (and cache) a MarianMT translation pipeline for a language pair."""
    model_id = _MARIAN_MODELS.get(lang_code)
    if not model_id:
        return None
    try:
        from transformers import pipeline

        logger.info("Loading MarianMT model for '%s': %s", lang_code, model_id)
        pipe = pipeline("translation", model=model_id)
        logger.info("Translation model for '%s' loaded.", lang_code)
        return pipe
    except Exception as exc:
        logger.warning("MarianMT load failed for '%s': %s", lang_code, exc)
        return None


def _translate_with_marian(text: str, lang_code: str) -> Optional[str]:
    """Translate using MarianMT. Returns None on failure."""
    pipe = _get_marian_pipeline(lang_code)
    if pipe is None:
        return None
    try:
        prefix = _MARIAN_LANG_TAGS.get(lang_code, "")
        input_text = f"{prefix} {text}" if prefix else text
        # MarianMT handles ~512 tokens; split long texts into chunks
        chunks = _split_into_chunks(input_text, max_words=400)
        translated_chunks = []
        for chunk in chunks:
            result = pipe(chunk, max_length=512)
            translated_chunks.append(result[0]["translation_text"])
        return " ".join(translated_chunks).strip()
    except Exception as exc:
        logger.warning("MarianMT translation failed for '%s': %s", lang_code, exc)
        return None


def _translate_with_googletrans(text: str, lang_code: str) -> Optional[str]:
    """Fallback: translate via googletrans library."""
    try:
        from googletrans import Translator

        translator = Translator()
        result = translator.translate(text, dest=lang_code)
        return result.text
    except Exception as exc:
        logger.warning("googletrans fallback failed for '%s': %s", lang_code, exc)
        return None


def _split_into_chunks(text: str, max_words: int = 400) -> list:
    """Split text into chunks of at most max_words words."""
    words = text.split()
    return [
        " ".join(words[i : i + max_words])
        for i in range(0, len(words), max_words)
    ]


def translate(text: str, target_lang: str) -> str:
    """
    Translate *text* into *target_lang*.

    Args:
        text: Source text in English.
        target_lang: ISO 639-1 language code ('hi', 'kn', 'ta').

    Returns:
        Translated string, or the original text with a fallback note.
    """
    if not text or not text.strip():
        return ""

    if target_lang == "en":
        return text  # no translation needed

    # Attempt 1: MarianMT
    result = _translate_with_marian(text, target_lang)
    if result:
        return result

    # Attempt 2: googletrans
    result = _translate_with_googletrans(text, target_lang)
    if result:
        return result

    # Final fallback
    logger.error("All translation methods failed for lang '%s'.", target_lang)
    return f"[Translation unavailable] {text}"


def translate_all(text: str) -> dict:
    """
    Translate text into all supported Indian languages.

    Returns:
        dict with keys 'hi', 'kn', 'ta' containing translated strings.
    """
    return {
        "hi": translate(text, "hi"),
        "kn": translate(text, "kn"),
        "ta": translate(text, "ta"),
    }
