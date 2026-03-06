"""
OCR Service — extracts text from PDFs, images, and plain text files.

Priority:
1. EasyOCR  (GPU-optional, good accuracy for printed documents)
2. pytesseract  (fallback if EasyOCR is unavailable)
3. pdfplumber  for native PDF text extraction
"""

import io
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def _extract_from_pdf(file_bytes: bytes) -> str:
    """Use pdfplumber to extract text from a PDF byte stream."""
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            pages = [page.extract_text() or "" for page in pdf.pages]
        text = "\n".join(pages).strip()
        if text:
            return text
    except Exception as exc:
        logger.warning("pdfplumber failed: %s", exc)

    # Fallback: render PDF pages as images and OCR them
    return _ocr_pdf_pages(file_bytes)


def _ocr_pdf_pages(file_bytes: bytes) -> str:
    """Render PDF pages to images and OCR each page."""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        texts = []
        for page in doc:
            pix = page.get_pixmap(dpi=200)
            img_bytes = pix.tobytes("png")
            texts.append(_ocr_image_bytes(img_bytes))
        return "\n".join(texts).strip()
    except Exception as exc:
        logger.warning("PyMuPDF OCR fallback failed: %s", exc)
        return ""


def _ocr_image_bytes(image_bytes: bytes) -> str:
    """OCR an image supplied as raw bytes — tries EasyOCR then Tesseract."""
    # --- EasyOCR ---
    try:
        import easyocr
        import numpy as np
        from PIL import Image

        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        reader = easyocr.Reader(["en"], gpu=False, verbose=False)
        results = reader.readtext(np.array(img), detail=0)
        text = " ".join(results).strip()
        if text:
            return text
    except Exception as exc:
        logger.warning("EasyOCR failed: %s", exc)

    # --- pytesseract ---
    try:
        from PIL import Image
        import pytesseract

        img = Image.open(io.BytesIO(image_bytes))
        return pytesseract.image_to_string(img).strip()
    except Exception as exc:
        logger.warning("pytesseract failed: %s", exc)

    return ""


def extract_text(file_bytes: bytes, filename: str) -> str:
    """
    Public entry point.  Detect file type from filename and extract text.

    Returns the extracted text string (may be empty if extraction fails).
    """
    suffix = Path(filename).suffix.lower()

    if suffix == ".txt":
        try:
            return file_bytes.decode("utf-8", errors="replace").strip()
        except Exception as exc:
            logger.error("Text decode error: %s", exc)
            return ""

    if suffix == ".pdf":
        return _extract_from_pdf(file_bytes)

    if suffix in {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"}:
        return _ocr_image_bytes(file_bytes)

    # Unknown — try text decode first, then image OCR
    try:
        decoded = file_bytes.decode("utf-8", errors="strict").strip()
        if decoded:
            return decoded
    except UnicodeDecodeError:
        pass
    return _ocr_image_bytes(file_bytes)
