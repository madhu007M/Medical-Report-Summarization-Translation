"""
Symptom-based Chatbot Service.

Provides a rule-based conversational chatbot that asks follow-up questions
based on the medical report content and user-reported symptoms.
"""

import re
import logging
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Question bank
# ---------------------------------------------------------------------------

_SYMPTOM_FOLLOWUP: dict[str, list[str]] = {
    "fever": [
        "How many days have you had the fever?",
        "What is your current temperature?",
        "Do you have chills or sweating along with the fever?",
        "Have you taken any medication for the fever?",
    ],
    "cough": [
        "Is your cough dry or producing mucus?",
        "How long have you been coughing?",
        "Do you experience chest pain while coughing?",
        "Have you noticed any blood in your cough?",
    ],
    "pain": [
        "Where exactly do you feel the pain?",
        "On a scale of 1–10, how severe is the pain?",
        "Is the pain constant or does it come and go?",
        "Does any movement or activity worsen the pain?",
    ],
    "breathing": [
        "Do you feel short of breath even at rest?",
        "Does the breathing difficulty worsen with activity?",
        "Are you experiencing chest tightness?",
        "Do you have a history of asthma or respiratory conditions?",
    ],
    "diabetes": [
        "Are you currently on diabetes medication?",
        "When did you last check your blood sugar?",
        "Have you experienced dizziness or sweating recently?",
        "Do you follow a specific diet plan?",
    ],
    "blood pressure": [
        "Do you regularly monitor your blood pressure at home?",
        "Are you on any blood pressure medications?",
        "Have you experienced headaches or dizziness recently?",
        "Do you consume a high-salt diet?",
    ],
    "anaemia": [
        "Do you often feel tired or weak?",
        "Have you noticed paleness in your skin or nails?",
        "Do you eat iron-rich foods like spinach, lentils, or meat?",
        "Are you currently taking iron supplements?",
    ],
}

_GENERAL_FOLLOWUP = [
    "Can you describe your main complaint in your own words?",
    "When did you first notice these symptoms?",
    "Do you have any known allergies or chronic conditions?",
    "Are you currently taking any medications?",
    "Have you had similar episodes in the past?",
]


def _detect_topics(text: str) -> list[str]:
    """Detect symptom/condition keywords in *text*."""
    topics = []
    text_lower = text.lower()
    for keyword in _SYMPTOM_FOLLOWUP:
        if keyword in text_lower:
            topics.append(keyword)
    return topics


def _get_bot_response(user_message: str, context_text: str, history: list[dict]) -> str:
    """Generate the next chatbot response."""
    user_lower = user_message.lower().strip()

    # Greetings
    if user_lower in {"hi", "hello", "hey", "start", "help"}:
        topics = _detect_topics(context_text)
        if topics:
            return (
                f"Hello! Based on your medical report I can see mentions of "
                f"{', '.join(topics)}. "
                f"I'll ask you a few follow-up questions to better understand your condition.\n\n"
                f"{_SYMPTOM_FOLLOWUP[topics[0]][0]}"
            )
        return (
            "Hello! I'm your medical report assistant. "
            "Please tell me your main symptom or concern so I can ask relevant follow-up questions."
        )

    # Detect topic from combined context + latest message
    combined = context_text + " " + user_message
    topics = _detect_topics(combined)

    if topics:
        # Find which questions have already been asked
        asked = {m["content"] for m in history if m.get("role") == "assistant"}
        for topic in topics:
            for question in _SYMPTOM_FOLLOWUP.get(topic, []):
                if question not in asked:
                    return question

    # Fall back to general questions
    asked = {m["content"] for m in history if m.get("role") == "assistant"}
    for q in _GENERAL_FOLLOWUP:
        if q not in asked:
            return q

    return (
        "Thank you for sharing that information. "
        "Based on your responses, I recommend consulting a qualified healthcare professional "
        "for a proper diagnosis and treatment plan. "
        "Is there anything else you would like to discuss?"
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def chat(
    user_message: str,
    context_text: str = "",
    history: list[dict] | None = None,
) -> dict[str, Any]:
    """
    Process a chat turn.

    Args:
        user_message:  Latest message from the user.
        context_text:  The extracted medical report text (for context).
        history:       List of previous messages [{'role': 'user'|'assistant', 'content': '...'}].

    Returns:
        {
            "response": str,       # Bot's reply
            "history": list[dict], # Updated conversation history
        }
    """
    history = history or []
    history.append({"role": "user", "content": user_message})

    response = _get_bot_response(user_message, context_text, history)
    history.append({"role": "assistant", "content": response})

    return {"response": response, "history": history}


def get_initial_greeting(context_text: str = "") -> str:
    """Return the opening message for a new chat session."""
    topics = _detect_topics(context_text)
    if topics:
        return (
            f"Hello! I've reviewed your medical report. I noticed some keywords related to "
            f"{', '.join(topics[:3])}. "
            f"I'll ask you a few questions to better understand your situation. "
            f"\n\n{_SYMPTOM_FOLLOWUP[topics[0]][0]}"
        )
    return (
        "Hello! I'm your medical report assistant. "
        "Please describe your main symptoms or concerns, and I'll help guide you."
    )
