"""Interactive Symptom Questioning Module — Context-Aware Health Assistant.

Analyzes medical reports to generate intelligent follow-up questions that help:
- Gather additional symptom details for better risk assessment
- Educate patients about their condition
- Guide appropriate next steps based on responses

Key features:
- Report-based question generation (detects conditions from text)
- Progressive questioning (starts broad, gets specific)
- Session-based conversation tracking
- Multi-language support via translation_module
- Risk-aware guidance (adapts advice to severity)
"""
import logging
import re
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════════════════════════
# CONDITION DETECTION — Extract health issues from medical report text
# ══════════════════════════════════════════════════════════════════════════════

_CONDITION_PATTERNS = {
    "fever": r"\b(fever|pyrexia|temp|temperature.*\d{2,3}\.?\d*\s*[CF])\b",
    "hypertension": r"\b(hypertension|high.*blood.*pressure|bp.*\d{3}/\d{2,3}|elevated.*bp)\b",
    "cough": r"\b(cough|productive.*cough|dry.*cough)\b",
    "respiratory": r"\b(shortness.*breath|dyspnea|breathing.*difficulty|wheezing)\b",
    "chest_pain": r"\b(chest.*pain|angina|cardiac.*pain)\b",
    "headache": r"\b(headache|migraine|cephalalgia)\b",
    "diabetes": r"\b(diabetes|diabetic|hyperglycemia|glucose.*\d{3,})\b",
    "infection": r"\b(infection|sepsis|bacteremia)\b",
    "anemia": r"\b(anemia|anaemia|low.*hemoglobin|hb.*\d\.?\d)\b",
}

_MEDICATION_KEYWORDS = {
    "paracetamol": "Use only the prescribed dose and avoid duplicate cold/flu medicines containing paracetamol.",
    "acetaminophen": "Use only the prescribed dose and avoid duplicate cold/flu medicines containing acetaminophen.",
    "ibuprofen": "Take after food and avoid if you have stomach ulcers, kidney disease, or are advised against NSAIDs.",
    "amoxicillin": "Complete the full antibiotic course and do not stop early unless your doctor advises.",
    "metformin": "Take with meals and monitor blood sugar regularly.",
    "insulin": "Follow prescribed timing and dose; monitor blood glucose and watch for low-sugar symptoms.",
    "amlodipine": "Take at a fixed daily time and monitor blood pressure regularly.",
    "losartan": "Take consistently and follow scheduled kidney and blood pressure monitoring.",
}


def _detect_conditions(report_text: str) -> List[str]:
    """Identify medical conditions mentioned in the report text.

    Returns a list of condition keys (e.g., ["fever", "hypertension"]).
    """
    text_lower = report_text.lower()
    detected = []

    for condition, pattern in _CONDITION_PATTERNS.items():
        if re.search(pattern, text_lower):
            detected.append(condition)

    return detected


def _extract_medications(text: str) -> List[str]:
    """Detect known medicine names in user text using simple keyword matching."""
    text_lower = text.lower()
    meds = [name for name in _MEDICATION_KEYWORDS if re.search(rf"\b{re.escape(name)}\b", text_lower)]
    return sorted(set(meds))


def generate_medication_guidance(user_message: str) -> Dict[str, object]:
    """Provide non-prescriptive medication guidance when medicine names appear."""
    meds = _extract_medications(user_message)
    if not meds:
        return {
            "medications_detected": [],
            "guidance": "",
        }

    lines = []
    for med in meds:
        tip = _MEDICATION_KEYWORDS.get(med)
        if tip:
            lines.append(f"{med.title()}: {tip}")

    lines.append("Do not change dose or stop prescribed medicine without medical advice.")
    return {
        "medications_detected": meds,
        "guidance": " ".join(lines),
    }


def predict_future_risks(symptoms: List[str], risk_level: str) -> List[str]:
    """Predict near-term health risk patterns from symptom keywords and risk level."""
    symptom_text = " ".join(s.lower() for s in symptoms)
    risks: List[str] = []

    if "chest pain" in symptom_text or "shortness of breath" in symptom_text:
        risks.append("Cardio-respiratory symptoms may worsen quickly; seek urgent in-person evaluation if persistent.")

    if "fever" in symptom_text and ("cough" in symptom_text or "body ache" in symptom_text):
        risks.append("Combined fever and respiratory/body symptoms can indicate infectious illness; monitor temperature and hydration closely.")

    if "dizziness" in symptom_text or "weakness" in symptom_text:
        risks.append("Persistent dizziness/weakness may increase fall and dehydration risk; avoid driving and monitor vitals.")

    if risk_level == "High":
        risks.append("Current high-risk profile suggests possible short-term deterioration; do not delay clinical care.")
    elif risk_level == "Moderate":
        risks.append("Moderate risk may progress if symptoms increase; arrange timely doctor follow-up.")

    return risks[:4]


def build_chat_insights(user_message: str, symptoms: List[str], risk_level: str) -> Dict[str, object]:
    """Bundle medication and future-risk insights for chatbot responses."""
    med = generate_medication_guidance(user_message)
    future_risks = predict_future_risks(symptoms, risk_level)
    return {
        "medications_detected": med["medications_detected"],
        "medication_guidance": med["guidance"],
        "future_risk_signals": future_risks,
    }


# ══════════════════════════════════════════════════════════════════════════════
# QUESTION TEMPLATES — Contextual follow-up questions for each condition
# ══════════════════════════════════════════════════════════════════════════════

_QUESTION_TEMPLATES = {
    "fever": [
        "How many days have you had the fever?",
        "What is your current temperature reading?",
        "Are you experiencing chills, sweating, or body aches?",
        "Have you taken any fever medication (like paracetamol or ibuprofen)?",
    ],
    "hypertension": [
        "Do you regularly monitor your blood pressure at home?",
        "Are you experiencing headaches, dizziness, or blurred vision?",
        "Are you currently taking any blood pressure medication?",
        "Do you have a family history of hypertension?",
    ],
    "cough": [
        "Is your cough dry or producing phlegm?",
        "Have you noticed any blood in the phlegm?",
        "How long have you had the cough?",
        "Is it interfering with your sleep?",
    ],
    "respiratory": [
        "Do you feel short of breath when resting or only during activity?",
        "Are you able to speak in full sentences without pausing for breath?",
        "Do you have any chest tightness or wheezing?",
        "Are you using any inhalers or oxygen support?",
    ],
    "chest_pain": [
        "Where exactly is the chest pain located?",
        "Does the pain radiate to your arm, jaw, or back?",
        "On a scale of 1-10, how severe is the pain?",
        "Does the pain worsen with deep breathing or movement?",
    ],
    "headache": [
        "How would you describe the headache (throbbing, sharp, dull)?",
        "Is it affecting one side of your head or both?",
        "Are you experiencing nausea, vomiting, or sensitivity to light?",
        "How often do you get these headaches?",
    ],
    "diabetes": [
        "Are you monitoring your blood sugar levels regularly?",
        "What was your most recent blood sugar reading?",
        "Are you experiencing increased thirst or frequent urination?",
        "Are you following a diabetic diet plan?",
    ],
    "infection": [
        "Do you have any wounds, cuts, or areas of redness and swelling?",
        "Are you experiencing fever along with other symptoms?",
        "Have you had any recent surgeries or medical procedures?",
        "Are you on any antibiotics currently?",
    ],
    "anemia": [
        "Do you feel unusually tired or weak?",
        "Are you experiencing dizziness when standing up?",
        "Have you noticed any paleness in your skin or inside your eyelids?",
        "Are you taking iron supplements or vitamin B12?",
    ],
}


# ══════════════════════════════════════════════════════════════════════════════
# CONVERSATION STATE MANAGEMENT
# ══════════════════════════════════════════════════════════════════════════════

class ConversationState:
    """Tracks conversation progress and patient responses."""

    def __init__(self):
        self.conditions: List[str] = []
        self.asked_questions: List[str] = []
        self.responses: Dict[str, str] = {}
        self.current_focus: Optional[str] = None  # Which condition we're asking about
        self.question_index: int = 0  # Which question in the current condition

    def add_response(self, question: str, answer: str):
        """Store patient's response to a question."""
        self.responses[question] = answer
        self.asked_questions.append(question)

    def get_next_question(self) -> Optional[Tuple[str, str]]:
        """Get next question based on current state.

        Returns: (condition, question) or (None, None) if done
        """
        # If no current focus, pick the first unprocessed condition
        if self.current_focus is None:
            if not self.conditions:
                return None, None
            self.current_focus = self.conditions[0]
            self.question_index = 0

        # Get questions for current condition
        questions = _QUESTION_TEMPLATES.get(self.current_focus, [])

        # If we've asked all questions for this condition, move to next
        if self.question_index >= len(questions):
            # Remove current condition from list
            self.conditions = [c for c in self.conditions if c != self.current_focus]
            self.current_focus = None
            self.question_index = 0
            return self.get_next_question()  # Recursive call for next condition

        # Return next question
        question = questions[self.question_index]
        self.question_index += 1
        return self.current_focus, question


# ══════════════════════════════════════════════════════════════════════════════
# PUBLIC API
# ══════════════════════════════════════════════════════════════════════════════

def analyze_report_and_generate_questions(
    report_text: str,
    risk_level: str = "Low",
    max_questions: int = 3,
) -> Dict[str, object]:
    """Analyze medical report and generate initial questions.

    Args:
        report_text: Full medical report text
        risk_level: Risk assessment level ("Low", "Moderate", "High")
        max_questions: Maximum number of questions to ask initially

    Returns:
        {
            "detected_conditions": [...],
            "questions": [...],
            "intro_message": "...",
            "urgency": "normal" | "urgent" | "emergency"
        }
    """
    conditions = _detect_conditions(report_text)

    # Determine urgency based on risk level
    urgency = "emergency" if risk_level == "High" else (
        "urgent" if risk_level == "Moderate" else "normal"
    )

    # Generate intro message based on detected conditions
    if not conditions:
        intro = "I've reviewed your report. To better understand your health, I'd like to ask a few questions."
    elif len(conditions) == 1:
        intro = f"I noticed your report mentions {conditions[0].replace('_', ' ')}. Let me ask some follow-up questions to understand your situation better."
    else:
        condition_list = ", ".join([c.replace("_", " ") for c in conditions[:2]])
        intro = f"Your report mentions several things including {condition_list}. I'll ask questions to help clarify your condition."

    # Generate questions (prioritize high-risk conditions)
    questions: List[Dict[str, str]] = []

    # High-priority conditions first
    priority_conditions = ["chest_pain", "respiratory", "infection"]
    sorted_conditions = [c for c in priority_conditions if c in conditions] + \
                       [c for c in conditions if c not in priority_conditions]

    for condition in sorted_conditions[:max_questions]:
        condition_questions = _QUESTION_TEMPLATES.get(condition, [])
        if condition_questions:
            questions.append({
                "condition": condition,
                "question": condition_questions[0],  # Start with first question
                "category": "initial_assessment",
            })

    # Fallback if no specific conditions detected
    if not questions:
        questions.append({
            "condition": "general",
            "question": "Are you currently experiencing any symptoms like fever, pain, or discomfort?",
            "category": "general_screening",
        })

    return {
        "detected_conditions": conditions,
        "questions": questions[:max_questions],
        "intro_message": intro,
        "urgency": urgency,
    }


def generate_follow_up_question(
    user_response: str,
    current_condition: str,
    conversation_history: List[Dict[str, str]],
) -> Optional[Dict[str, str]]:
    """Generate next follow-up question based on user's response.

    Args:
        user_response: Patient's answer to previous question
        current_condition: Condition being discussed
        conversation_history: List of {"question": "...", "answer": "..."}

    Returns:
        {"condition": "...", "question": "...", "is_final": bool} or None if done
    """
    # Get remaining questions for this condition
    all_questions = _QUESTION_TEMPLATES.get(current_condition, [])
    asked_questions = [item["question"] for item in conversation_history]
    remaining = [q for q in all_questions if q not in asked_questions]

    # Limit to 3-4 questions per condition to avoid fatigue
    if len([q for q in asked_questions if q in all_questions]) >= 3:
        logger.info("Asked enough questions for %s, moving on", current_condition)
        return None

    if not remaining:
        return None

    # Return next question
    return {
        "condition": current_condition,
        "question": remaining[0],
        "is_final": len(remaining) == 1,
    }


def generate_response(
    user_message: str,
    context: Optional[Dict[str, object]] = None,
) -> str:
    """Generate intelligent response based on user's message and context.

    Args:
        user_message: Patient's message or answer
        context: Optional context including:
            - current_condition: str
            - risk_level: str
            - conversation_history: List[Dict]

    Returns:
        Contextual response string
    """
    context = context or {}
    message_lower = user_message.lower()
    current_condition = context.get("current_condition", "")
    risk_level = context.get("risk_level", "Low")

    # ── Emergency indicators ──────────────────────────────────────────────────
    emergency_keywords = ["severe", "unbearable", "can't breathe", "chest pain", "unconscious"]
    if any(kw in message_lower for kw in emergency_keywords):
        return ("⚠️ Based on what you've shared, this could be serious. "
                "Please seek immediate medical attention or call emergency services.")

    # ── Condition-specific responses ──────────────────────────────────────────
    if current_condition == "fever":
        if "high" in message_lower or any(temp in message_lower for temp in ["103", "104", "105"]):
            return ("A fever above 102°F requires medical attention. "
                    "Take fever-reducing medication and consult a doctor if it persists.")
        return "Monitor your temperature every 4-6 hours. Stay well-hydrated and rest."

    elif current_condition == "hypertension":
        if "yes" in message_lower or "headache" in message_lower or "dizzy" in message_lower:
            return ("These symptoms with high blood pressure can be concerning. "
                    "Please check with your doctor soon and monitor your BP daily.")
        return "Continue monitoring your blood pressure and follow your prescribed treatment plan."

    elif current_condition == "cough":
        if "blood" in message_lower:
            return ("🩸 Coughing up blood requires immediate medical evaluation. "
                    "Please visit a doctor or hospital as soon as possible.")
        if "dry" in message_lower:
            return "A dry cough can be managed with warm fluids and honey. If it persists beyond a week, consult a doctor."
        return "For a productive cough, stay hydrated and consider using steam inhalation."

    elif current_condition == "respiratory":
        if "rest" in message_lower:
            return ("Shortness of breath at rest is a red flag. "
                    "Please seek medical care immediately.")
        return "Difficulty breathing should be evaluated by a healthcare provider, especially if worsening."

    elif current_condition == "chest_pain":
        if any(word in message_lower for word in ["arm", "jaw", "shoulder", "severe"]):
            return ("🚨 Chest pain radiating to arm/jaw could indicate a heart problem. "
                    "Go to the ER or call emergency services immediately.")
        return "Any chest pain should be evaluated by a doctor to rule out serious causes."

    # ── General acknowledgment ────────────────────────────────────────────────
    if risk_level == "High":
        return "Thank you for sharing. Given your report results, I recommend consulting with a healthcare provider soon."
    elif risk_level == "Moderate":
        return "I understand. Keep monitoring your symptoms and follow up with your doctor if they worsen."
    else:
        return "Thank you for the information. This helps me understand your situation better."


# ══════════════════════════════════════════════════════════════════════════════
# BACKWARD COMPATIBILITY — Keep old functions for existing endpoint
# ══════════════════════════════════════════════════════════════════════════════

def next_questions(symptoms: List[str]) -> List[str]:
    """Legacy function for basic symptom screening."""
    prompts: List[str] = []
    for symptom in symptoms:
        condition_questions = _QUESTION_TEMPLATES.get(symptom.lower(), [])
        if condition_questions:
            prompts.extend(condition_questions[:2])  # First 2 questions per symptom

    if not prompts:
        prompts.append("Are you experiencing any symptoms like fever, cough, chest pain, or dizziness?")

    return prompts[:5]  # Limit to 5 total questions
