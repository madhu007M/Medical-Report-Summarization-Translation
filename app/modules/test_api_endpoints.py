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
    def test_process_report_endpoint(
        self,
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

    def test_audio_stream_endpoint_synthesis_failure(self, client):
        """Audio stream handles synthesis failure."""
        response = client.get("/audio/explanation?text=&language=en")
        assert response.status_code in [200, 500]

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
