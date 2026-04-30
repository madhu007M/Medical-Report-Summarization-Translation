"""Tests for summarizer module with fallbacks."""
from unittest.mock import MagicMock, patch

import pytest

from backend.app.modules import summarizer_module


class TestSummarizerModule:
    """Medical text summarization with fallback handling."""

    @patch("backend.app.modules.summarizer_module._get_summarizer")
    def test_simplify_report_success(self, mock_get_summarizer):
        """Successful summarization returns summary."""
        mock_tokenizer = MagicMock()
        mock_model = MagicMock()
        # Tokenizer returns a dict-like object; model.generate returns ids
        mock_tokenizer.return_value = {"input_ids": MagicMock()}
        mock_model.generate.return_value = [[0]]
        mock_tokenizer.decode.return_value = "Patient has fever and cough. Rest recommended."
        mock_get_summarizer.return_value = (mock_tokenizer, mock_model)

        text = "Patient presents with high fever (103F) and persistent cough for 3 days."
        result = summarizer_module.simplify_report(text, "facebook/bart-large-cnn")

        assert "summary" in result
        assert len(result["summary"]) > 0

    @patch("backend.app.modules.summarizer_module._get_summarizer")
    def test_simplify_report_model_failure(self, mock_get_summarizer):
        """Model failure triggers smart extractor fallback."""
        mock_get_summarizer.side_effect = Exception("Model loading failed")

        text = "Patient Name: John. Chief Complaint: Fever for 3 days. Temperature: 102F."
        result = summarizer_module.simplify_report(text, "facebook/bart-large-cnn")

        assert "summary" in result
        # Smart extractor should produce structured output
        assert "📋" in result["summary"] or "Patient" in result["summary"] or len(result["summary"]) > 10

    @patch("backend.app.modules.summarizer_module._get_summarizer")
    def test_simplify_report_empty_text(self, mock_get_summarizer):
        """Empty text falls through to smart extractor which handles it."""
        mock_get_summarizer.side_effect = Exception("Model not available")

        result = summarizer_module.simplify_report("", "facebook/bart-large-cnn")
        assert "summary" in result
        assert "No health report" in result["summary"]

    @patch("backend.app.modules.summarizer_module._get_summarizer")
    def test_simplify_report_short_text(self, mock_get_summarizer):
        """Short text is handled by smart extractor when model unavailable."""
        mock_get_summarizer.side_effect = Exception("Model not available")

        text = "Short medical note about fever."
        result = summarizer_module.simplify_report(text, "facebook/bart-large-cnn")
        assert "summary" in result
        assert len(result["summary"]) > 0
