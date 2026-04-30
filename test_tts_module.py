"""Tests for text-to-speech module."""
from unittest.mock import MagicMock, patch

import pytest

from backend.app.modules import tts_module


class TestTTSModule:
    """audio generation and streaming."""

    @patch("backend.app.modules.tts_module.gTTS")
    def test_synthesize_audio_bytes_success(self, mock_gtts):
        """Successful audio synthesis returns bytes."""
        mock_tts = MagicMock()
        mock_gtts.return_value = mock_tts

        audio_fp = MagicMock()
        audio_fp.getvalue.return_value = b"fake_mp3_header"
        mock_tts.write_to_fp = MagicMock()

        result = tts_module.synthesize_audio_bytes("Test text", "en")
        assert isinstance(result, bytes)

    @patch("backend.app.modules.tts_module.gTTS")
    def test_synthesize_audio_bytes_success_hindi(self, mock_gtts):
        """Audio synthesis in Hindi."""
        mock_tts = MagicMock()
        mock_gtts.return_value = mock_tts

        audio_fp = MagicMock()
        result = tts_module.synthesize_audio_bytes("बुखार है", "hi")
        assert isinstance(result, bytes)

    @patch("backend.app.modules.tts_module.gTTS")
    def test_synthesize_audio_bytes_failure(self, mock_gtts):
        """Synthesis failure returns empty bytes."""
        mock_gtts.side_effect = Exception("TTS service error")

        result = tts_module.synthesize_audio_bytes("Test text", "en")
        assert result == b""

    @patch("backend.app.modules.tts_module.synthesize_audio_bytes")
    def test_synthesize_audio_file_success(self, mock_synth_bytes):
        """Legacy file-based synthesis."""
        mock_synth_bytes.return_value = b"fake_mp3_data"

        result = tts_module.synthesize_audio("Test text", "en")
        assert isinstance(result, str)
        assert "explanation_" in result
        # Verify audio_bytes was called
        mock_synth_bytes.assert_called_once()

    @patch("backend.app.modules.tts_module.gTTS")
    def test_synthesize_audio_file_failure(self, mock_gtts):
        """File synthesis failure returns empty string."""
        mock_gtts.side_effect = Exception("TTS service error")

        result = tts_module.synthesize_audio("Test text", "en")
        assert result == ""

    @patch("backend.app.modules.tts_module.gTTS")
    def test_synthesize_multiple_languages(self, mock_gtts):
        """Support multiple language codes."""
        mock_tts = MagicMock()
        mock_gtts.return_value = mock_tts

        for lang in ["en", "hi", "kn", "ta"]:
            result = tts_module.synthesize_audio_bytes("Text", lang)
            assert isinstance(result, bytes)
            mock_gtts.assert_called()

    def test_expand_medical_abbreviations(self):
        """Medical abbreviations are expanded correctly."""
        text = "BP: 120/80, HR: 72, Temp: 98.6F"
        result = tts_module._expand_medical_abbreviations(text)
        assert "blood pressure" in result.lower()
        assert "heart rate" in result.lower()
        assert "temperature" in result.lower()
        # Slash should become 'over'
        assert "over" in result.lower()

    def test_clean_for_speech(self):
        """Text cleaning removes URLs and normalizes whitespace."""
        text = "Patient report   available at https://example.com/report.pdf  BP: 130/85"
        result = tts_module._clean_for_speech(text)
        assert "https://" not in result
        assert "link removed" in result
        assert "blood pressure" in result.lower()
        # Whitespace normalized
        assert "  " not in result

    def test_chunk_text_for_tts_short(self):
        """Short text returns single chunk."""
        text = "This is a short sentence."
        chunks = tts_module._chunk_text_for_tts(text, max_chars=1000)
        assert len(chunks) == 1
        assert chunks[0] == text

    def test_chunk_text_for_tts_long(self):
        """Long text is chunked at sentence boundaries."""
        # Create text > 100 chars with multiple sentences
        text = "First sentence here. " * 10 + "Second sentence here. " * 10
        chunks = tts_module._chunk_text_for_tts(text, max_chars=100)
        # Should split into multiple chunks
        assert len(chunks) > 1
        # All content preserved
        assert " ".join(chunks) == text

    @patch("backend.app.modules.tts_module.gTTS")
    def test_synthesize_with_slow_mode(self, mock_gtts):
        """Slow mode parameter is passed to gTTS."""
        mock_tts = MagicMock()
        mock_gtts.return_value = mock_tts

        tts_module.synthesize_audio_bytes("Test text", "en", slow=True)

        # Verify gTTS was called with slow=True
        call_args = mock_gtts.call_args
        assert call_args.kwargs.get("slow") == True

    @patch("backend.app.modules.tts_module.gTTS")
    def test_synthesize_with_tld_mapping(self, mock_gtts):
        """Language TLD mapping is applied for better voices."""
        mock_tts = MagicMock()
        mock_gtts.return_value = mock_tts

        # Hindi should use co.in TLD
        tts_module.synthesize_audio_bytes("Test text", "hi")

        call_args = mock_gtts.call_args
        assert call_args.kwargs.get("tld") == "co.in"

    @patch("backend.app.modules.tts_module.gTTS")
    def test_synthesize_sentences(self, mock_gtts):
        """Sentence-by-sentence synthesis returns list."""
        mock_tts = MagicMock()
        mock_gtts.return_value = mock_tts

        text = "First sentence. Second sentence. Third sentence."
        results = tts_module.synthesize_sentences(text, "en")

        assert len(results) == 3
        assert all("text" in r and "audio_bytes" in r for r in results)
        assert results[0]["index"] == 0
        assert "First sentence" in results[0]["text"]

    def test_synthesize_empty_text(self):
        """Empty text returns empty bytes."""
        result = tts_module.synthesize_audio_bytes("", "en")
        assert result == b""

        result = tts_module.synthesize_audio_bytes("   ", "en")
        assert result == b""
