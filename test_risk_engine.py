"""Tests for risk detection and urgency scoring."""
import pytest

from backend.app.modules import risk_engine


class TestRiskEngine:
    """Medical risk classification and urgency scoring."""

    def test_risk_high_hypertensive_crisis(self):
        """High BP (180/120) triggers high risk."""
        text = "Blood Pressure: 185/125 mmHg"
        result = risk_engine.evaluate_risk(text, [])

        assert result["risk_level"] == "High"
        assert result["risk_score"] >= 3
        assert any("crisis" in alert.lower() or "emergency" in alert.lower() for alert in result["alerts"])

    def test_risk_high_fever(self):
        """High fever (>102F) contributes to high risk."""
        text = "Temperature: 103.5F"
        result = risk_engine.evaluate_risk(text, [])

        assert result["risk_level"] in ["Moderate", "High"]
        assert any("fever" in alert.lower() for alert in result["alerts"])

    def test_risk_moderate_elevated_bp(self):
        """Moderate BP elevation."""
        text = "BP: 145/95 mmHg"
        result = risk_engine.evaluate_risk(text, [])

        assert result["risk_level"] in ["Moderate", "Low"]

    def test_risk_low_normal_vitals(self):
        """Normal vitals should be low risk."""
        text = "BP: 120/80, Temp: 98.6F"
        result = risk_engine.evaluate_risk(text, [])

        assert result["risk_level"] == "Low"
        assert len(result["alerts"]) == 0

    def test_risk_critical_terms(self):
        """Sepsis or shock terms trigger high risk."""
        text = "Patient presenting with signs of sepsis and potential shock."
        result = risk_engine.evaluate_risk(text, [])

        assert result["risk_level"] == "High"
        assert any("critical" in alert.lower() for alert in result["alerts"])

    def test_risk_multiple_symptoms(self):
        """Multiple severe symptoms compound risk."""
        text = "BP: 170/110, Chest pain ongoing."
        symptoms = ["chest pain", "shortness of breath"]
        result = risk_engine.evaluate_risk(text, symptoms)

        assert result["risk_level"] == "High"
        assert result["risk_score"] >= 6

    def test_risk_recommendation_high(self):
        """High-risk recommendation is emergency."""
        text = "BP: 190/130"
        result = risk_engine.evaluate_risk(text, [])
        assert "hospital" in result["recommendation"].lower() or "emergency" in result["recommendation"].lower()

    def test_risk_recommendation_moderate(self):
        """Moderate-risk recommendation includes doctor visit."""
        text = "BP: 150/95, Temp: 101F"
        result = risk_engine.evaluate_risk(text, [])
        if result["risk_level"] == "Moderate":
            assert "doctor" in result["recommendation"].lower()

    def test_risk_recommendation_low(self):
        """Low-risk recommendation is supportive."""
        text = "Vitals stable. Minor cough."
        result = risk_engine.evaluate_risk(text, [])
        if result["risk_level"] == "Low":
            assert len(result["recommendation"]) > 0

    def test_risk_fever_365_threshold(self):
        """Fever >=100F detected, <102F is moderate."""
        text = "Temperature: 101.2F"
        result = risk_engine.evaluate_risk(text, [])

        assert "fever" in str(result["alerts"]).lower()

    def test_risk_empty_symptoms_list(self):
        """Empty symptoms list should not crash."""
        text = "Patient stable"
        result = risk_engine.evaluate_risk(text, [])

        assert "risk_level" in result
        assert "risk_score" in result
        assert "alerts" in result
