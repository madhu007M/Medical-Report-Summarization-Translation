"""
Tests for the AI Medical Report Interpreter Platform.

These unit tests validate core business logic (OCR helpers, risk service,
chatbot service, and location service) without requiring external ML models,
a live database, or network access.
"""

import sys
import os

# Ensure the project root is on sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest


# ===========================================================================
# Risk Service Tests
# ===========================================================================

class TestRiskService:
    """Tests for the rule-based medical risk analysis service."""

    def test_high_glucose_returns_high_risk(self):
        from backend.services.risk_service import analyse_risk

        text = "Blood glucose: 220 mg/dL"
        result = analyse_risk(text)
        assert result["risk_level"] == "High"
        assert result["risk_score"] >= 3

    def test_normal_glucose_returns_low_risk(self):
        from backend.services.risk_service import analyse_risk

        text = "Blood glucose: 95 mg/dL"
        result = analyse_risk(text)
        assert "glucose" in result["details"]
        assert result["details"]["glucose"]["level"] == "Low"

    def test_moderate_glucose_returns_moderate(self):
        from backend.services.risk_service import analyse_risk

        text = "Fasting blood glucose: 160 mg/dL"
        result = analyse_risk(text)
        assert result["details"]["glucose"]["level"] == "Moderate"

    def test_severe_anaemia(self):
        from backend.services.risk_service import analyse_risk

        text = "Haemoglobin: 6.5 g/dL"
        result = analyse_risk(text)
        assert result["details"]["hemoglobin"]["level"] == "High"

    def test_normal_hemoglobin(self):
        from backend.services.risk_service import analyse_risk

        text = "Hemoglobin: 13.5 g/dL"
        result = analyse_risk(text)
        assert result["details"]["hemoglobin"]["level"] == "Low"

    def test_high_blood_pressure(self):
        from backend.services.risk_service import analyse_risk

        text = "Blood pressure: 185/120 mmHg"
        result = analyse_risk(text)
        assert result["details"]["bp"]["level"] == "High"

    def test_normal_blood_pressure(self):
        from backend.services.risk_service import analyse_risk

        text = "BP: 120/80 mmHg"
        result = analyse_risk(text)
        assert result["details"]["bp"]["level"] == "Low"

    def test_high_fever(self):
        from backend.services.risk_service import analyse_risk

        text = "Temperature: 104.5 F"
        result = analyse_risk(text)
        assert result["details"]["temperature"]["level"] == "High"

    def test_low_spo2_emergency(self):
        from backend.services.risk_service import analyse_risk

        text = "SpO2: 88%"
        result = analyse_risk(text)
        assert result["details"]["spo2"]["level"] == "High"

    def test_normal_spo2(self):
        from backend.services.risk_service import analyse_risk

        text = "SpO2: 98%"
        result = analyse_risk(text)
        assert result["details"]["spo2"]["level"] == "Low"

    def test_high_risk_symptoms_raise_score(self):
        from backend.services.risk_service import analyse_risk

        result = analyse_risk("", symptoms=["chest pain", "difficulty breathing"])
        # 2 high-risk symptoms = 6 pts → risk should be High
        assert result["risk_level"] == "High"

    def test_empty_text_returns_low(self):
        from backend.services.risk_service import analyse_risk

        result = analyse_risk("", symptoms=[])
        assert result["risk_level"] == "Low"
        assert result["risk_score"] == 0.0

    def test_recommendations_present(self):
        from backend.services.risk_service import analyse_risk

        result = analyse_risk("Blood glucose: 250 mg/dL")
        assert len(result["recommendations"]) > 0

    def test_result_keys(self):
        from backend.services.risk_service import analyse_risk

        result = analyse_risk("Normal report with no abnormal values.")
        assert "risk_level" in result
        assert "risk_score" in result
        assert "details" in result
        assert "recommendations" in result


# ===========================================================================
# Chatbot Service Tests
# ===========================================================================

class TestChatbotService:
    """Tests for the rule-based symptom chatbot."""

    def test_greeting_returns_string(self):
        from backend.services.chatbot_service import chat

        result = chat("hello", context_text="", history=[])
        assert isinstance(result["response"], str)
        assert len(result["response"]) > 0

    def test_history_updated(self):
        from backend.services.chatbot_service import chat

        result = chat("hello")
        # History should contain the user message and assistant response
        roles = [m["role"] for m in result["history"]]
        assert "user" in roles
        assert "assistant" in roles

    def test_fever_context_triggers_followup(self):
        from backend.services.chatbot_service import chat

        result = chat("I have a fever", context_text="Patient reports fever and high temperature.")
        # Should ask a follow-up about fever
        response_lower = result["response"].lower()
        assert any(kw in response_lower for kw in ["fever", "temperature", "days", "chills"])

    def test_initial_greeting_with_context(self):
        from backend.services.chatbot_service import get_initial_greeting

        greeting = get_initial_greeting("Patient has diabetes and high glucose levels.")
        assert "diabetes" in greeting.lower() or "glucose" in greeting.lower() or "?" in greeting

    def test_initial_greeting_without_context(self):
        from backend.services.chatbot_service import get_initial_greeting

        greeting = get_initial_greeting("")
        assert isinstance(greeting, str)
        assert len(greeting) > 10

    def test_history_accumulates(self):
        from backend.services.chatbot_service import chat

        r1 = chat("hello")
        r2 = chat("I have a cough", history=r1["history"])
        # After two turns, history should have at least 4 entries
        assert len(r2["history"]) >= 4

    def test_all_history_exhausted_returns_summary(self):
        """After all follow-up questions are asked, chatbot gives a closing message."""
        from backend.services.chatbot_service import chat

        history = []
        context = "fever cough pain breathing diabetes blood pressure anaemia"
        # 7 topics × 4 questions + 5 general = 33 total questions; use 40 turns to ensure exhaustion
        for _ in range(40):
            r = chat("yes", context_text=context, history=history)
            history = r["history"]

        last_response = history[-1]["content"].lower()
        # Eventually should reach the closing recommendation
        assert any(kw in last_response for kw in ["healthcare", "consult", "anything", "doctor"])


# ===========================================================================
# Location / Outbreak Service Tests
# ===========================================================================

class TestLocationService:
    """Tests for disease inference and outbreak detection logic."""

    def test_dengue_inference(self):
        from backend.services.location_service import infer_disease

        symptoms = ["fever", "rash", "joint pain", "headache"]
        disease = infer_disease(symptoms)
        assert disease == "dengue"

    def test_flu_inference(self):
        from backend.services.location_service import infer_disease

        symptoms = ["fever", "cough", "fatigue", "body ache"]
        disease = infer_disease(symptoms)
        assert disease == "flu"

    def test_covid_inference(self):
        from backend.services.location_service import infer_disease

        symptoms = ["fever", "cough", "loss of taste", "fatigue"]
        disease = infer_disease(symptoms)
        assert disease == "covid"

    def test_no_match_returns_none(self):
        from backend.services.location_service import infer_disease

        disease = infer_disease(["itchy eyes"])
        assert disease is None

    def test_single_symptom_no_match(self):
        from backend.services.location_service import infer_disease

        disease = infer_disease(["fever"])
        # A single symptom matching multiple diseases should not return a match
        # (threshold is >=2 overlapping symptoms)
        assert disease is None

    def test_empty_symptoms(self):
        from backend.services.location_service import infer_disease

        assert infer_disease([]) is None


# ===========================================================================
# OCR Service Tests (text-file path only — no image/ML dependencies needed)
# ===========================================================================

class TestOcrServiceTextPath:
    """Tests for the plain-text extraction path of the OCR service."""

    def test_extract_plain_text(self):
        from backend.services.ocr_service import extract_text

        content = "Patient Name: John Doe\nDiagnosis: Normal\nGlucose: 95 mg/dL"
        result = extract_text(content.encode("utf-8"), "report.txt")
        assert "John Doe" in result
        assert "Glucose" in result

    def test_empty_text_file(self):
        from backend.services.ocr_service import extract_text

        result = extract_text(b"", "empty.txt")
        assert result == ""

    def test_utf8_encoding(self):
        from backend.services.ocr_service import extract_text

        content = "रिपोर्ट सारांश"
        result = extract_text(content.encode("utf-8"), "report.txt")
        assert "रिपोर्ट" in result


# ===========================================================================
# Summarizer Tests (rule-based fallback path)
# ===========================================================================

class TestSummarizerFallback:
    """Tests for the rule-based summarization fallback."""

    def test_empty_returns_message(self):
        from backend.services.summarizer import summarize

        result = summarize("")
        assert "No text" in result or len(result) > 0

    def test_rule_based_extracts_keywords(self):
        """When the AI model is unavailable, the rule-based fallback should
        extract sentences with medical keywords."""
        from backend.services import summarizer

        # Force fallback by calling _rule_based_summary directly
        text = (
            "The patient presents with elevated glucose levels. "
            "Diagnosis: Type 2 Diabetes. "
            "Recommended treatment: metformin 500 mg twice daily. "
            "Follow up in 3 months."
        )
        result = summarizer._rule_based_summary(text)
        assert "glucose" in result.lower() or "diagnosis" in result.lower() or "treatment" in result.lower()

    def test_truncation(self):
        from backend.services.summarizer import _truncate_text

        long_text = " ".join(["word"] * 1000)
        truncated = _truncate_text(long_text, max_words=700)
        assert len(truncated.split()) == 700


# ===========================================================================
# Messaging Service Tests (no Twilio credentials required)
# ===========================================================================

class TestMessagingServiceNoCredentials:
    """Tests that messaging service returns graceful errors without credentials."""

    def test_sms_without_credentials(self):
        from backend.services.messaging_service import send_sms

        result = send_sms("+919876543210", "Test message")
        assert result["success"] is False
        assert result["error"] is not None

    def test_whatsapp_without_credentials(self):
        from backend.services.messaging_service import send_whatsapp

        result = send_whatsapp("+919876543210", "Test message")
        assert result["success"] is False

    def test_broadcast_returns_list(self):
        from backend.services.messaging_service import broadcast_alert

        results = broadcast_alert(["+919876543210", "+919876543211"], "Test", "Body")
        assert isinstance(results, list)
        assert len(results) == 2
        for r in results:
            assert "success" in r
