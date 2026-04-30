"""OCR Module — Medical Report Text Extraction.

Supports plain text, PDF (native + scanned), PNG/JPG images.
Applies image preprocessing to improve accuracy for medical documents.
"""
import io
import logging
import re
from typing import Optional

import PyPDF2
from PIL import Image, ImageEnhance, ImageFilter
from fastapi import UploadFile

try:
    import pytesseract
except ImportError:  # pragma: no cover - optional dependency
    pytesseract = None

logger = logging.getLogger(__name__)

# Tesseract config: PSM 6 = assume uniform block of text (good for medical reports)
_OCR_CONFIG = "--psm 6 --oem 3"

# Minimum character count to consider PDF text extraction successful
_PDF_MIN_CHARS = 50


def _initialize_tesseract() -> None:
    """Configure Tesseract executable path if set in environment."""
    from ..config import get_settings
    settings = get_settings()
    if settings.tesseract_cmd_path and pytesseract:
        pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd_path
        logger.info("Tesseract path configured: %s", settings.tesseract_cmd_path)


def _load_image(file_bytes: bytes) -> Image.Image:
    """Load a PIL Image from raw bytes. Kept separate for testability."""
    return Image.open(io.BytesIO(file_bytes))


def _preprocess_image(image: Image.Image) -> Image.Image:
    """Enhance image quality for better OCR accuracy on medical documents.

    Steps applied:
    1. Convert to grayscale - removes color noise that confuses OCR.
    2. Boost contrast  - makes faint printed text clearly visible.
    3. Sharpen edges   - improves character boundary detection.
    """
    # 1. Grayscale
    image = image.convert("L")
    # 2. Contrast boost (factor 2.0 works well for scanned medical docs)
    image = ImageEnhance.Contrast(image).enhance(2.0)
    # 3. Edge sharpening
    image = image.filter(ImageFilter.SHARPEN)
    return image


def _clean_text(text: str) -> str:
    """Normalize raw OCR output to remove common artifacts.

    - Collapses multiple blank lines into one paragraph break.
    - Removes stray single non-alphanumeric characters (OCR noise).
    - Strips leading/trailing whitespace.
    """
    # Collapse 3+ newlines → double newline (paragraph break)
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Collapse multiple spaces/tabs → single space
    text = re.sub(r'[ \t]+', ' ', text)
    # Remove lines that contain only 1-2 non-word characters (OCR noise artifacts)
    text = re.sub(r'(?m)^\s*[^a-zA-Z0-9\n]{1,2}\s*$', '', text)
    return text.strip()


def _extract_from_image(file_bytes: bytes) -> str:
    """Run full OCR pipeline: load → preprocess → extract → clean."""
    image = _load_image(file_bytes)
    processed = _preprocess_image(image)
    raw_text = pytesseract.image_to_string(processed, config=_OCR_CONFIG)
    return _clean_text(raw_text)


def _read_pdf_bytes(file_bytes: bytes) -> str:
    """Extract text from a PDF.

    Strategy:
    1. Try native PyPDF2 text extraction (works for digital PDFs).
    2. If result is too short (< _PDF_MIN_CHARS), the PDF is likely a scanned
       image. In that case, attempt page-by-page OCR using pymupdf (fitz) if
       available.
    3. Always clean and return the best result found.
    """
    reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
    pages_text = [page.extract_text() or "" for page in reader.pages]
    combined = _clean_text("\n".join(pages_text))

    if len(combined) >= _PDF_MIN_CHARS or not pytesseract:
        return combined

    # Scanned PDF — attempt OCR via pymupdf
    logger.info("PDF text too short (%d chars); attempting image OCR", len(combined))
    try:
        import fitz  # type: ignore  # pymupdf optional dependency
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        ocr_pages = []
        for page in doc:
            pix = page.get_pixmap(dpi=200)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            processed = _preprocess_image(img)
            ocr_pages.append(
                pytesseract.image_to_string(processed, config=_OCR_CONFIG)
            )
        return _clean_text("\n".join(ocr_pages))
    except ImportError:
        logger.info("pymupdf not available; returning native PDF text")
    except Exception as exc:
        logger.exception("Scanned PDF OCR failed: %s", exc)

    return combined


def extract_text(upload: UploadFile) -> str:
    """Extract and clean text from an uploaded medical report.

    Supported formats:
    - text/plain, text/markdown  → direct UTF-8 decode
    - application/pdf            → PyPDF2 + fallback OCR for scanned PDFs
    - image/* (PNG, JPG, etc.)   → Tesseract OCR with preprocessing

    Falls back to raw bytes decode for any unsupported or unreadable files.
    """
    _initialize_tesseract()

    file_bytes = upload.file.read()
    content_type = upload.content_type or ""

    try:
        if content_type in {"text/plain", "text/markdown"}:
            return file_bytes.decode(errors="ignore")

        if content_type == "application/pdf":
            return _read_pdf_bytes(file_bytes)

        if content_type.startswith("image/") and pytesseract:
            return _extract_from_image(file_bytes)

    except Exception as exc:  # pragma: no cover - runtime safety net
        logger.exception("OCR extraction failed for %s: %s", content_type, exc)

    # Fallback: best-effort raw byte decode
    logger.warning("Using raw-bytes fallback for content type: %s", content_type)
    return _clean_text(file_bytes.decode(errors="ignore"))
