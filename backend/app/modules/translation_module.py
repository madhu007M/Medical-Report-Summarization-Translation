"""Translation Module — Multilingual Medical Report Explanation.

Supports English, Hindi, Kannada, Tamil, Telugu, Marathi, Bengali.

Key design decisions:
- lru_cache keeps each HuggingFace pipeline alive across requests (avoids
  repeated 500 MB model loads).
- Long texts are split at sentence boundaries before translation so the
  transformer never sees more than ~400 characters at once (preventing
  silent truncation at max_length=512 tokens).
- Falls back to the original text on any error so patients always see
  something useful.
"""
import logging
import re
from functools import lru_cache
from typing import Dict, List

from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

logger = logging.getLogger(__name__)

# Display names for every supported language (used by the frontend)
LANGUAGE_MAP: Dict[str, str] = {
    "en": "English",
    "hi": "Hindi (हिन्दी)",
    "kn": "Kannada (ಕನ್ನಡ)",
    "ta": "Tamil (தமிழ்)",
    "te": "Telugu (తెలుగు)",
    "mr": "Marathi (मराठी)",
    "bn": "Bengali (বাংলা)",
}

# Common aliases accepted from frontend/user input.
_LANGUAGE_ALIASES: Dict[str, str] = {
    "english": "en",
    "en-us": "en",
    "en-in": "en",
    "common": "en",
    "simple": "en",
    "plain": "en",
    "hindi": "hi",
    "kannada": "kn",
    "tamil": "ta",
    "telugu": "te",
    "marathi": "mr",
    "bengali": "bn",
    "bangla": "bn",
}

# Maximum characters per chunk sent to the model.
# Helsinki-NLP models handle ~400 ASCII characters comfortably within
# the 512-token limit for typical medical prose.
_CHUNK_MAX_CHARS = 400

# Helsinki-NLP opus-mt-en-mul requires an inline >>lang<< prefix token to
# select the output language. These are ISO 639-3 codes the model was trained on.
_MUL_LANGUAGE_TOKENS: Dict[str, str] = {
    "ta": ">>tam<< ",
    "te": ">>tel<< ",
    "kn": ">>kan<< ",
    "mr": ">>mar<< ",
}
_MULTILINGUAL_MODEL_NAMES = {"Helsinki-NLP/opus-mt-en-mul"}


@lru_cache(maxsize=16)
def _get_translator(model_name: str):
    """Load (and cache) a Helsinki-NLP translation model directly.

    Uses AutoTokenizer + AutoModelForSeq2SeqLM to bypass the broken
    pipeline task registry in transformers 5.x.
    Returns None for the identity (English pass-through) model.
    """
    logger.info("Loading translation model: %s", model_name)
    if model_name == "identity":
        return None
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    return tokenizer, model


def _split_sentences(text: str) -> List[str]:
    """Split text on sentence-ending punctuation (.  !  ?) followed by whitespace."""
    parts = re.split(r'(?<=[.!?])\s+', text.strip())
    return [p.strip() for p in parts if p.strip()]


def _chunk_text(text: str, max_chars: int = _CHUNK_MAX_CHARS) -> List[str]:
    """Group sentences into chunks that each stay under max_chars.

    Prevents long medical reports from being silently truncated by the
    transformer tokeniser.  Sentences longer than max_chars on their own
    are passed through as single chunks (minor overruns are better than
    a hard mid-sentence cut).
    """
    sentences = _split_sentences(text)
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


def normalize_target_language(target_language: str, translation_models: Dict[str, str]) -> str:
    """Normalize human-friendly language input to a configured language code.

    Accepts language codes ("hi"), language names ("Hindi"), locale-like values
    ("en-IN") and aliases ("common", "simple"). Falls back to English when
    available, otherwise to the first configured language.
    """
    if not target_language:
        return "en" if "en" in translation_models else next(iter(translation_models), "en")

    raw = target_language.strip().lower()
    if raw in translation_models:
        return raw

    # Normalize locale-like input (e.g., en-IN -> en).
    if "-" in raw:
        base = raw.split("-", 1)[0]
        if base in translation_models:
            return base

    # Match exact aliases first.
    alias_code = _LANGUAGE_ALIASES.get(raw)
    if alias_code and alias_code in translation_models:
        return alias_code

    # Match by display-name token before parenthesis (e.g., "Hindi (हिन्दी)").
    for code, display_name in LANGUAGE_MAP.items():
        canonical = display_name.split("(", 1)[0].strip().lower()
        if raw == canonical and code in translation_models:
            return code

    return "en" if "en" in translation_models else next(iter(translation_models), "en")


def translate_text(text: str, target_language: str, translation_models: Dict[str, str]) -> str:
    """Translate text into target_language using the configured model.

    Long texts are split into sentence-level chunks so no content is lost
    to the model's token limit.  All chunks are translated and joined.

    Returns the original text unchanged when:
    - target_language is "en" (identity pass-through)
    - the language has no configured model
    - an error occurs during translation
    """
    try:
        normalized_language = normalize_target_language(target_language, translation_models)
        model_name = translation_models.get(normalized_language, "identity")
        translator = _get_translator(model_name)

        if translator is None:
            return text

        tokenizer, model = translator

        # Multilingual models need a ">>lang<<" inline prefix on each chunk.
        lang_prefix = ""
        if model_name in _MULTILINGUAL_MODEL_NAMES:
            lang_prefix = _MUL_LANGUAGE_TOKENS.get(normalized_language, "")

        chunks = _chunk_text(text)
        translated_chunks: List[str] = []

        for chunk in chunks:
            prefixed = lang_prefix + chunk
            inputs = tokenizer(
                prefixed,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512,
            )
            outputs = model.generate(**inputs)
            translated_chunks.append(tokenizer.decode(outputs[0], skip_special_tokens=True))

        return " ".join(translated_chunks)

    except Exception as exc:
        logger.exception("Translation to '%s' failed: %s", target_language, exc)
        return text


def list_supported_languages(translation_models: Dict[str, str]) -> List[Dict[str, str]]:
    """Return display info for every language that has a configured model."""
    return [
        {"code": code, "name": LANGUAGE_MAP.get(code, code)}
        for code in translation_models
    ]
