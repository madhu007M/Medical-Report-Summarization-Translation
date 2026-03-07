"""Tests for translation module with fallbacks."""
from unittest.mock import MagicMock, patch

import pytest

from backend.app.modules import translation_module


class TestTranslationModule:
    """Multilingual text translation with graceful degradation."""

    @patch("backend.app.modules.translation_module._get_translator")
    def test_translate_text_success(self, mock_get_translator):
        """Successful translation."""
        mock_tokenizer = MagicMock()
        mock_model = MagicMock()
        mock_tokenizer.return_value = {"input_ids": MagicMock()}
        mock_model.generate.return_value = [[0]]
        mock_tokenizer.decode.return_value = "बुखार और खांसी दोनों मौजूद हैं।"
        mock_get_translator.return_value = (mock_tokenizer, mock_model)

        models = {"hi": "Helsinki-NLP/opus-mt-en-hi", "en": "identity"}
        result = translation_module.translate_text("Fever and cough present.", "hi", models)

        assert len(result) > 0

    @patch("backend.app.modules.translation_module._get_translator")
    def test_translate_text_identity_passthrough(self, mock_get_translator):
        """Identity model returns unchanged text."""
        mock_get_translator.return_value = None

        models = {"en": "identity"}
        text = "Fever and cough present."
        result = translation_module.translate_text(text, "en", models)

        assert result == text

    @patch("backend.app.modules.translation_module._get_translator")
    def test_translate_text_unsupported_language(self, mock_get_translator):
        """Unsupported language falls back to identity."""
        mock_get_translator.return_value = None

        models = {"en": "identity"}
        text = "Fever and cough present."
        result = translation_module.translate_text(text, "fr", models)

        assert result == text

    @patch("backend.app.modules.translation_module._get_translator")
    def test_translate_text_model_failure(self, mock_get_translator):
        """Model error returns original text."""
        mock_tokenizer = MagicMock()
        mock_model = MagicMock()
        mock_model.generate.side_effect = Exception("Translation failed")
        mock_tokenizer.return_value = {"input_ids": MagicMock()}
        mock_get_translator.return_value = (mock_tokenizer, mock_model)

        models = {"hi": "Helsinki-NLP/opus-mt-en-hi"}
        text = "Fever and cough present."
        result = translation_module.translate_text(text, "hi", models)

        assert result == text

    @patch("backend.app.modules.translation_module._get_translator")
    def test_translate_text_model_load_failure(self, mock_get_translator):
        """Model load error should return original text instead of raising."""
        mock_get_translator.side_effect = Exception("Model download failed")

        models = {"ta": "Helsinki-NLP/opus-mt-en-ta"}
        text = "Take rest and drink water."
        result = translation_module.translate_text(text, "ta", models)

        assert result == text

    @patch("backend.app.modules.translation_module._get_translator")
    def test_translate_text_kannada(self, mock_get_translator):
        """Kannada translation."""
        mock_tokenizer = MagicMock()
        mock_model = MagicMock()
        mock_tokenizer.return_value = {"input_ids": MagicMock()}
        mock_model.generate.return_value = [[0]]
        mock_tokenizer.decode.return_value = "ಜ್ವರ ಮತ್ತು ಕಾಸು ಇವೆ."
        mock_get_translator.return_value = (mock_tokenizer, mock_model)

        models = {"kn": "Helsinki-NLP/opus-mt-en-mul"}
        result = translation_module.translate_text("Fever and cough.", "kn", models)
        assert len(result) > 0

    @patch("backend.app.modules.translation_module._get_translator")
    def test_translate_text_tamil(self, mock_get_translator):
        """Tamil translation."""
        mock_tokenizer = MagicMock()
        mock_model = MagicMock()
        mock_tokenizer.return_value = {"input_ids": MagicMock()}
        mock_model.generate.return_value = [[0]]
        mock_tokenizer.decode.return_value = "காய்ச்சல் மற்றும் இருமல் உள்ளது."
        mock_get_translator.return_value = (mock_tokenizer, mock_model)

        models = {"ta": "Helsinki-NLP/opus-mt-en-ta"}
        result = translation_module.translate_text("Fever and cough.", "ta", models)
        assert len(result) > 0

    def test_chunk_text_short(self):
        """Short text returns single chunk."""
        text = "This is a short sentence."
        chunks = translation_module._chunk_text(text, max_chars=100)
        assert len(chunks) == 1
        assert chunks[0] == text

    def test_chunk_text_multiple_sentences(self):
        """Long text with multiple sentences splits correctly."""
        # Create text with 3 sentences that should split into 2 chunks
        s1 = "This is the first sentence with enough words to matter."
        s2 = "This is the second sentence also fairly long."
        s3 = "This is the third sentence."
        text = f"{s1} {s2} {s3}"

        chunks = translation_module._chunk_text(text, max_chars=80)
        # Should split: s1+s2 exceeds 80, so s1 alone, then s2+s3
        assert len(chunks) >= 2
        # All original text should be preserved
        assert " ".join(chunks) == text

    def test_chunk_text_preserves_content(self):
        """Chunking preserves all text content."""
        text = "Sentence one. Sentence two. Sentence three. Sentence four. Sentence five."
        chunks = translation_module._chunk_text(text, max_chars=50)
        reconstructed = " ".join(chunks)
        assert reconstructed == text

    @patch("backend.app.modules.translation_module._get_translator")
    def test_translate_text_with_chunking(self, mock_get_translator):
        """Long text is chunked and each chunk is translated."""
        call_count = {"n": 0}
        mock_tokenizer = MagicMock()
        mock_model = MagicMock()
        mock_tokenizer.return_value = {"input_ids": MagicMock()}

        def decode_side_effect(ids, skip_special_tokens=True):
            call_count["n"] += 1
            return f"Hindi chunk {call_count['n']}."

        mock_model.generate.return_value = [[0]]
        mock_tokenizer.decode.side_effect = decode_side_effect
        mock_get_translator.return_value = (mock_tokenizer, mock_model)

        # Create long text that will be split
        text = "A" * 300 + ". " + "B" * 300 + "."
        models = {"hi": "Helsinki-NLP/opus-mt-en-hi"}
        result = translation_module.translate_text(text, "hi", models)

        # Should have called model.generate more than once (one per chunk)
        assert mock_model.generate.call_count >= 1
        assert len(result) > 0

    def test_list_supported_languages(self):
        """List supported languages returns correct structure."""
        models = {
            "en": "identity",
            "hi": "Helsinki-NLP/opus-mt-en-hi",
            "ta": "Helsinki-NLP/opus-mt-en-ta",
        }
        languages = translation_module.list_supported_languages(models)

        assert len(languages) == 3
        assert all("code" in lang and "name" in lang for lang in languages)
        codes = [lang["code"] for lang in languages]
        assert "en" in codes
        assert "hi" in codes
        assert "ta" in codes
