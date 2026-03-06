"""
Translation API — on-demand translation of text.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.config import SUPPORTED_LANGUAGES
from backend.services import translator

router = APIRouter(prefix="/translate", tags=["Translation"])


class TranslateRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Text to translate (in English)")
    target_lang: str = Field(..., description="Target language code: 'hi', 'kn', or 'ta'")


class TranslateAllRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Text to translate (in English)")


@router.post("/", summary="Translate text into a single target language")
def translate_text(req: TranslateRequest):
    if req.target_lang not in SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported target language '{req.target_lang}'. Supported: {list(SUPPORTED_LANGUAGES.keys())}",
        )
    translated = translator.translate(req.text, req.target_lang)
    return {
        "original": req.text,
        "translated": translated,
        "language": req.target_lang,
        "language_name": SUPPORTED_LANGUAGES[req.target_lang],
    }


@router.post("/all", summary="Translate text into all supported languages")
def translate_all(req: TranslateAllRequest):
    translations = translator.translate_all(req.text)
    return {
        "original": req.text,
        "translations": {
            lang: {"text": text, "language_name": SUPPORTED_LANGUAGES.get(lang, lang)}
            for lang, text in translations.items()
        },
    }


@router.get("/languages", summary="List supported languages")
def list_languages():
    return {"languages": SUPPORTED_LANGUAGES}
