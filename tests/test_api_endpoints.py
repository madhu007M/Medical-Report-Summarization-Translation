"""Integration tests for FastAPI endpoints."""
import io
from unittest.mock import patch

import pytest


class TestAPIEndpoints:
    """Full API contract tests."""

    def test_health_endpoint(self, client):
        """Health check should return 200."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    @patch("backend.app.modules.ocr_module.extract_text")
    @patch("backend.app.modules.summarizer_module.simplify_report")
    @patch("backend.app.modules.risk_engine.evaluate_risk")
    @patch("backend.app.modules.translation_module.translate_text")
    @patch("backend.app.modules.chatbot_module.analyze_report_and_generate_questions")
    def test_process_report_endpoint(
        self,
        mock_follow_up,
        mock_translate,
        mock_risk,
        mock_summarize,
        mock_ocr,
        client,
        test_db,
    ):
        """Process report endpoint processes file and returns result."""
        mock_ocr.return_value = "Patient has fever."
        mock_summarize.return_value = {"summary": "Fever detected."}
        mock_risk.return_value = {
            "risk_level": "Moderate",
            "risk_score": 2,
            "alerts": [],
            "recommendation": "See doctor",
        }
        mock_translate.return_value = "Fever detected."
        mock_follow_up.return_value = {
            "detected_conditions": ["fever"],
            "questions": [{"condition": "fever", "question": "How many days have you had fever?", "category": "initial_assessment"}],
            "intro_message": "Let me ask follow-up questions.",
            "urgency": "urgent",
        }

        file_data = io.BytesIO(b"Patient report")
        response = client.post(
            "/process-report",
            data={
                "language": "en",
                "phone": "",
                "location": "Mumbai",
                "symptoms": "fever",
            },
            files={"file": ("report.txt", file_data, "text/plain")},
        )

        assert response.status_code == 200
        data = response.json()
        assert "report_id" in data
        assert data["summary"] == "Fever detected."
        assert data["risk"]["risk_level"] == "Moderate"
        assert "audio_url" in data
        assert "follow_up" in data
        assert "questions" in data["follow_up"]

    def test_process_report_missing_file(self, client):
        """Missing file should return 422."""
        response = client.post(
            "/process-report",
            data={
                "language": "en",
                "phone": "",
                "location": "Mumbai",
                "symptoms": "",
            },
        )
        assert response.status_code == 422

    @patch("backend.app.modules.chatbot_module.generate_response")
    @patch("backend.app.modules.chatbot_module.next_questions")
    def test_chatbot_endpoint(self, mock_questions, mock_response, client):
        """Chatbot endpoint returns questions and response."""
        mock_questions.return_value = ["How long have you had fever?", "Any body ache?"]
        mock_response.return_value = "Please consult a doctor if symptoms persist."

        response = client.post(
            "/chatbot",
            json={
                "session_id": "test-session",
                "message": "I have fever",
                "symptoms": ["fever"],
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "prompts" in data
        assert "response" in data
        assert "insights" in data
        assert len(data["prompts"]) > 0

    def test_outbreaks_endpoint(self, client, test_db):
        """Outbreaks endpoint returns clusters."""
        response = client.get("/outbreaks?region=")
        assert response.status_code == 200
        data = response.json()
        assert "clusters" in data

    def test_outbreaks_with_region_filter(self, client, test_db):
        """Outbreaks with region filter."""
        response = client.get("/outbreaks?region=Mumbai")
        assert response.status_code == 200
        data = response.json()
        assert "clusters" in data

    def test_create_doctor_alert(self, client, test_db):
        """Create doctor alert."""
        response = client.post(
            "/doctor/alerts",
            json={
                "doctor_name": "Dr. Sharma",
                "region": "Mumbai",
                "title": "Dengue Alert",
                "message": "High dengue cases reported in the area.",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data

    def test_list_doctor_alerts(self, client, test_db):
        """List doctor alerts."""
        # Create an alert first
        client.post(
            "/doctor/alerts",
            json={
                "doctor_name": "Dr. Sharma",
                "region": "Mumbai",
                "title": "Dengue Alert",
                "message": "High dengue cases reported.",
            },
        )

        # List alerts
        response = client.get("/doctor/alerts?region=")
        assert response.status_code == 200
        data = response.json()
        assert "alerts" in data

    def test_list_doctor_alerts_region_filter(self, client, test_db):
        """List doctor alerts with region filter."""
        response = client.get("/doctor/alerts?region=Mumbai")
        assert response.status_code == 200
        data = response.json()
        assert "alerts" in data

    @patch("backend.app.modules.tts_module.synthesize_audio_bytes")
    def test_audio_stream_endpoint(self, mock_tts, client):
        """Audio stream endpoint returns MP3 bytes with correct content-type."""
        mock_tts.return_value = b"fake_mp3_data"

        response = client.get("/audio/explanation?text=Fever&language=en")
        assert response.status_code == 200
        # httpx Response uses headers, not .media_type / .body
        assert "audio/mpeg" in response.headers["content-type"]
        assert response.content == b"fake_mp3_data"

    @patch("backend.app.modules.tts_module.synthesize_audio_bytes")
    def test_audio_stream_endpoint_with_slow_mode(self, mock_tts, client):
        """Audio endpoint supports slow mode parameter."""
        mock_tts.return_value = b"fake_slow_mp3"

        response = client.get("/audio/explanation?text=Test&language=en&slow=true")
        assert response.status_code == 200
        # Verify slow parameter was passed to TTS module
        mock_tts.assert_called_with("Test", "en", True)

    def test_audio_stream_endpoint_synthesis_failure(self, client):
        """Audio stream handles synthesis failure."""
        response = client.get("/audio/explanation?text=&language=en")
        assert response.status_code in [200, 500]

    @patch("backend.app.modules.tts_module.synthesize_sentences")
    def test_audio_sentences_endpoint(self, mock_synth, client):
        """Sentence audio endpoint returns formatted JSON."""
        mock_synth.return_value = [
            {"index": 0, "text": "First sentence.", "audio_bytes": b"audio1", "char_count": 15},
            {"index": 1, "text": "Second sentence.", "audio_bytes": b"audio2", "char_count": 16},
        ]

        response = client.get("/audio/sentences?text=First%20sentence.%20Second%20sentence.&language=en")
        assert response.status_code == 200
        data = response.json()
        assert "sentences" in data
        assert data["total"] == 2
        # Audio bytes should be base64 encoded
        assert "audio_base64" in data["sentences"][0]
        # Original audio_bytes key should be removed
        assert "audio_bytes" not in data["sentences"][0]

    @patch("backend.app.modules.ocr_module.extract_text")
    def test_extract_text_endpoint(self, mock_ocr, client):
        """Extract-text endpoint returns OCR result and metadata."""
        mock_ocr.return_value = "Patient has high blood pressure."

        file_data = io.BytesIO(b"dummy content")
        response = client.post(
            "/extract-text",
            files={"file": ("report.txt", file_data, "text/plain")},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["extracted_text"] == "Patient has high blood pressure."
        assert data["char_count"] == len("Patient has high blood pressure.")
        assert data["filename"] == "report.txt"

    def test_languages_endpoint(self, client):
        """Languages endpoint returns list of supported languages."""
        response = client.get("/languages")
        assert response.status_code == 200
        data = response.json()
        assert "languages" in data
        assert len(data["languages"]) > 0
        # Check structure
        for lang in data["languages"]:
            assert "code" in lang
            assert "name" in lang

    @patch("backend.app.modules.translation_module.translate_text")
    def test_translate_endpoint(self, mock_translate, client):
        """Translate endpoint translates text on demand."""
        mock_translate.return_value = "बुखार का पता चला।"

        response = client.post(
            "/translate",
            json={"text": "Fever detected.", "target_language": "hi"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["original_text"] == "Fever detected."
        assert data["translated_text"] == "बुखार का पता चला।"
        assert data["target_language"] == "hi"
        assert data["requested_language"] == "hi"
        mock_translate.assert_called_once()

    @patch("backend.app.modules.translation_module.translate_text")
    def test_translate_endpoint_with_language_name(self, mock_translate, client):
        """Translate endpoint accepts human-friendly language labels."""
        mock_translate.return_value = "பரிசோதனை"

        response = client.post(
            "/translate",
            json={"text": "Test", "target_language": "Tamil"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["target_language"] == "ta"
        assert data["requested_language"] == "Tamil"

    @patch("backend.app.modules.ocr_module.extract_text")
    @patch("backend.app.modules.summarizer_module.simplify_report")
    @patch("backend.app.modules.risk_engine.evaluate_risk")
    @patch("backend.app.modules.translation_module.translate_text")
    @patch("backend.app.modules.chatbot_module.analyze_report_and_generate_questions")
    def test_process_report_returns_common_and_resolved_language(
        self,
        mock_follow_up,
        mock_translate,
        mock_risk,
        mock_summarize,
        mock_ocr,
        client,
        test_db,
    ):
        """Process-report should expose common summary and normalized language."""
        mock_ocr.return_value = "Patient has fever."
        mock_summarize.return_value = {"summary": "Common summary"}
        mock_risk.return_value = {
            "risk_level": "Low",
            "risk_score": 1,
            "alerts": [],
            "recommendation": "Hydrate",
        }
        mock_translate.return_value = "தமிழ் சுருக்கம்"
        mock_follow_up.return_value = {
            "detected_conditions": [],
            "questions": [],
            "intro_message": "",
            "urgency": "routine",
        }

        file_data = io.BytesIO(b"Patient report")
        response = client.post(
            "/process-report",
            data={
                "language": "Tamil",
                "phone": "",
                "location": "Chennai",
                "symptoms": "",
            },
            files={"file": ("report.txt", file_data, "text/plain")},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["summary"] == "தமிழ் சுருக்கம்"
        assert data["summary_common"] == "Common summary"
        assert data["language_requested"] == "Tamil"
        assert data["language_resolved"] == "ta"
        assert data["summary_by_language"]["en"] == "Common summary"
        assert data["summary_by_language"]["ta"] == "தமிழ் சுருக்கம்"
