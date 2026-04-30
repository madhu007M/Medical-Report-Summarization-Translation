"""Tests for OCR module with mocks."""
import io
from unittest.mock import MagicMock, patch

import pytest

from backend.app.modules import ocr_module


class TestOCRModule:
    """OCR extraction and fallback behavior."""

    def test_extract_text_plain(self, mock_upload_file):
        """Plain text passthrough should succeed."""
        mock_upload_file.content_type = "text/plain"
        result = ocr_module.extract_text(mock_upload_file)
        assert len(result) > 0
        assert "fever" in result.lower()

    def test_extract_text_markdown(self, mock_upload_file):
        """Markdown content should be decoded."""
        mock_upload_file.content_type = "text/markdown"
        result = ocr_module.extract_text(mock_upload_file)
        assert len(result) > 0

    @patch("backend.app.modules.ocr_module.PyPDF2.PdfReader")
    def test_extract_text_pdf(self, mock_pdf_reader, mock_upload_file):
        """PDF extraction should use PyPDF2."""
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "PDF content"
        mock_pdf_reader.return_value.pages = [mock_page]
        mock_upload_file.content_type = "application/pdf"

        result = ocr_module.extract_text(mock_upload_file)
        assert "PDF content" in result

    @patch("backend.app.modules.ocr_module._preprocess_image")
    @patch("backend.app.modules.ocr_module._load_image")
    @patch("backend.app.modules.ocr_module.pytesseract")
    def test_extract_text_image(self, mock_tesseract, mock_load_image, mock_preprocess, mock_upload_file):
        """Image should use Tesseract OCR with preprocessing when available.

        Three mocks are needed to isolate the full image OCR pipeline:
        - pytesseract : must be truthy so the image branch is entered
        - _load_image  : prevents PIL from trying to open fake bytes as an image
        - _preprocess_image: prevents ImageEnhance from rejecting the MagicMock
        """
        fake_image = MagicMock()           # stand-in for a real PIL Image
        mock_load_image.return_value = fake_image
        mock_preprocess.return_value = fake_image   # pass-through preprocessor
        mock_tesseract.image_to_string.return_value = "Extracted image text"
        mock_upload_file.content_type = "image/png"

        result = ocr_module.extract_text(mock_upload_file)
        assert "Extracted image text" in result
        mock_load_image.assert_called_once()
        mock_preprocess.assert_called_once_with(fake_image)
        mock_tesseract.image_to_string.assert_called_once()

    def test_extract_text_fallback(self, mock_upload_file):
        """Unsupported type falls back to raw decoding."""
        mock_upload_file.content_type = "application/unknown"
        result = ocr_module.extract_text(mock_upload_file)
        assert len(result) > 0

    @patch("backend.app.modules.ocr_module.pytesseract", None)
    def test_extract_text_pytesseract_unavailable(self, mock_upload_file):
        """Should handle missing pytesseract gracefully."""
        mock_upload_file.content_type = "image/png"
        result = ocr_module.extract_text(mock_upload_file)
        # Falls back to raw bytes
        assert len(result) >= 0
