import os
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Settings:
    """Application configuration values."""

    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./health_platform.db")
    ocr_engine: str = os.getenv("OCR_ENGINE", "pytesseract")
    tesseract_cmd_path: Optional[str] = os.getenv("TESSERACT_CMD_PATH", None)
    summarizer_model: str = os.getenv("SUMMARIZER_MODEL", "facebook/bart-large-cnn")
    translation_models: dict = None
    supported_languages: List[str] = None
    tts_provider: str = os.getenv("TTS_PROVIDER", "gtts")
    twilio_sid: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    twilio_token: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    twilio_from: str = os.getenv("TWILIO_FROM_NUMBER", "")
    outbreak_threshold: int = int(os.getenv("OUTBREAK_CLUSTER_THRESHOLD", "5"))

    def __post_init__(self) -> None:
        if self.translation_models is None:
            self.translation_models = {
                "hi": os.getenv("TRANSLATOR_HI_MODEL", "Helsinki-NLP/opus-mt-en-hi"),
                "kn": os.getenv("TRANSLATOR_KN_MODEL", "Helsinki-NLP/opus-mt-en-mul"),
                "ta": os.getenv("TRANSLATOR_TA_MODEL", "Helsinki-NLP/opus-mt-en-mul"),
                "te": os.getenv("TRANSLATOR_TE_MODEL", "Helsinki-NLP/opus-mt-en-mul"),
                "mr": os.getenv("TRANSLATOR_MR_MODEL", "Helsinki-NLP/opus-mt-en-mul"),
                "bn": os.getenv("TRANSLATOR_BN_MODEL", "Helsinki-NLP/opus-mt-en-bn"),
                "en": "identity",
            }
        if self.supported_languages is None:
            self.supported_languages = list(self.translation_models.keys())


def get_settings() -> Settings:
    return Settings()
