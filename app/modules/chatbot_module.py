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
    "fever": r"\b(fever|pyrexia|temp(erature)?|febrile|\d{2,3}\.?\d*\s*[CF]|high temp)\b",
    "hypertension": r"\b(hypertension|high.{0,10}blood.{0,10}pressure|bp.{0,10}\d{3}/\d{2,3}|elevated.{0,10}bp|blood pressure)\b",
    "cough": r"\b(cough(ing)?|productive.{0,10}cough|dry.{0,10}cough|whooping)\b",
    "respiratory": r"\b(shortness.{0,10}breath|dyspnea|breathing.{0,10}(difficulty|problem)|wheezing|breathless(ness)?|can.t breathe)\b",
    "chest_pain": r"\b(chest.{0,10}(pain|tightness|discomfort|pressure)|angina|cardiac.{0,10}pain|heart.{0,10}pain)\b",
    "headache": r"\b(headache|migraine|cephalalgia|head.{0,5}pain|head.{0,5}ache)\b",
    "diabetes": r"\b(diabetes|diabetic|hyperglycemia|glucose.{0,10}\d{3,}|blood.{0,5}sugar|hba1c|insulin.{0,10}(resistance|dependent))\b",
    "infection": r"\b(infection|sepsis|bacteremia|infected|pus|abscess)\b",
    "anemia": r"\b(anemia|anaemia|low.{0,10}hemoglobin|low.{0,10}haemoglobin|hb.{0,5}\d\.?\d|iron.{0,10}deficien)\b",
    "vomiting": r"\b(vomit(ing)?|nausea|nauseated|throwing.{0,5}up|puke|puking)\b",
    "diarrhea": r"\b(diarr?h(o?e?a)|loose.{0,5}stool|loose.{0,5}motion|watery.{0,5}stool)\b",
    "stomach": r"\b(stomach.{0,10}(pain|ache|cramp)|abdominal.{0,10}pain|belly.{0,10}pain|tummy.{0,10}(pain|ache)|gastric|indigestion)\b",
    "acidity": r"\b(acidity|heartburn|acid.{0,10}reflux|gerd|burning.{0,10}(chest|throat|stomach)|sour.{0,10}belch|gas.{0,10}trouble)\b",
    "constipation": r"\b(constipation|constipated|no.{0,10}bowel|hard.{0,10}stool|not.{0,10}passing.{0,10}stool|difficult.{0,10}bowel)\b",
    "joint_pain": r"\b(joint.{0,10}pain|arthritis|knee.{0,10}pain|body.{0,10}ache|muscle.{0,10}pain|myalgia|elbow.{0,10}pain|wrist.{0,10}pain)\b",
    "skin": r"\b(rash|skin.{0,10}(itch|problem)|hives|urticaria|allergic.{0,10}reaction|eczema|psoriasis|blisters)\b",
    "kidney": r"\b(kidney|renal|uti|burning.{0,10}urin(e|ation)|creatinine|frequent.{0,10}urin|blood.{0,10}urin|kidney.{0,10}stone)\b",
    "liver": r"\b(jaundice|hepatitis|liver.{0,10}(problem|disease|failure)|bilirubin|yellow.{0,10}(skin|eyes)|sgpt|sgot|alt|ast)\b",
    "thyroid": r"\b(thyroid|tsh|hypothyroid|hyperthyroid|thyroxine|goitre|goiter)\b",
    "mental_health": r"\b(anxiety|anxious|depression|depressed|stress(ed)?|panic.{0,10}attack|mental.{0,10}health|suicid|self.{0,5}harm)\b",
    "dengue": r"\b(dengue|breakbone.{0,10}fever|ns1|platelet.{0,10}(low|drop|count)|dengue.{0,10}fever)\b",
    "malaria": r"\b(malaria|malarial|plasmodium|falciparum|vivax|intermittent.{0,10}fever)\b",
    "typhoid": r"\b(typhoid|enteric.{0,10}fever|salmonella|widal)\b",
    "cold_flu": r"\b(cold|flu|influenza|runny.{0,10}nose|blocked.{0,10}nose|stuffy.{0,10}nose|sneezing|sore.{0,10}throat|body.{0,10}ache.{0,10}cold)\b",
    "sore_throat": r"\b(sore.{0,10}throat|throat.{0,10}pain|tonsil|strep|pharyngitis|difficulty.{0,10}swallow)\b",
    "dizziness": r"\b(dizzy|dizziness|vertigo|lightheaded|spinning|balance.{0,10}(issue|problem)|bhrama)\b",
    "ear": r"\b(ear.{0,10}(pain|ache|infection|discharge|ringing)|earache|tinnitus|hearing.{0,10}(loss|problem))\b",
    "palpitations": r"\b(palpitation|heart.{0,10}(racing|pounding|flutter|skip)|irregular.{0,10}heart|tachycardia|arrhythmia)\b",
    "swelling": r"\b(swell(ing|en)?|edema|oedema|water.{0,10}retention|puffy|puffiness|bloat(ing|ed))\b",
    "bleeding": r"\b(bleed(ing)?|hemorrhage|blood.{0,10}(loss|flow|stool|urine|vomit)|heavy.{0,10}bleed)\b",
    "fainting": r"\b(faint(ing|ed)?|syncope|passed.{0,5}out|blackout|lost.{0,5}consciousness|sudden.{0,5}fall)\b",
    "numbness": r"\b(numb(ness)?|tingling|pins.{0,5}needles|nerve.{0,10}pain|neurop|paralys|weakness.{0,5}limb)\b",
    "weight_loss": r"\b(weight.{0,10}loss|losing.{0,10}weight|unexplained.{0,10}weight|drastic.{0,10}weight)\b",
    "covid": r"\b(covid|corona(virus)?|covid.19|omicron|loss.{0,10}(smell|taste)|long.{0,5}covid)\b",
    "asthma": r"\b(asthma|asthmatic|inhaler|bronchospasm|broncho)\b",
    "dental": r"\b(tooth|teeth|toothache|dental|gum.{0,10}(pain|bleed)|cavity|wisdom.{0,10}tooth)\b",
    "urinary": r"\b(urin(e|ation|ary)|frequent.{0,10}urin|urge.{0,10}urin|burning.{0,10}urin|incontinence)\b",
    "allergy": r"\b(allerg(y|ic|en)|sneezing.{0,10}allerg|dust.{0,10}allerg|food.{0,10}allerg|seasonal.{0,10}allerg|hay.{0,10}fever)\b",
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
    """Generate intelligent response based on user's message and context."""
    context = context or {}
    message_lower = user_message.lower().strip()
    risk_level = str(context.get("risk_level", "Low"))

    # Auto-detect ALL matching conditions from message text
    current_condition = str(context.get("current_condition", "") or "")
    matched_conditions: List[str] = []
    if not current_condition:
        for condition, pattern in _CONDITION_PATTERNS.items():
            if re.search(pattern, message_lower, re.IGNORECASE):
                matched_conditions.append(condition)
        if matched_conditions:
            current_condition = matched_conditions[0]
    else:
        matched_conditions = [current_condition]

    # ── Emergency indicators ──────────────────────────────────────────────────
    emergency_keywords = [
        "unbearable", "can't breathe", "cannot breathe", "crushing chest",
        "unconscious", "heart attack", "stroke", "seizure", "fit",
        "collapse", "collapsed", "no pulse", "not breathing", "bleeding heavily",
        "severe chest", "paralysis", "paralysed", "sudden blindness",
        "severe head", "worst headache", "slurred speech",
    ]
    if any(kw in message_lower for kw in emergency_keywords):
        return (
            "⚠️ This sounds like a medical emergency. Please call emergency services immediately "
            "(108 in India / 112 for all emergencies). Do not wait — go to the nearest hospital now. "
            "If the person is unconscious, place them on their side and do not give food or water."
        )

    # ── Greeting / general query ──────────────────────────────────────────────
    greeting_keywords = ["hello", "hi", "hey", "good morning", "good evening", "good afternoon", "namaste", "hii", "helo"]
    if any(kw in message_lower for kw in greeting_keywords) and not current_condition:
        return (
            "Hello! I'm your AI health assistant. I can help you understand your medical report, "
            "explain symptoms, answer questions about medicines, lab values, diet, and lifestyle. "
            "Feel free to ask me anything — for example: 'I have fever for 3 days', "
            "'What does my BP reading mean?', or 'What is dengue?'"
        )

    # ── Help / capability questions ───────────────────────────────────────────
    if re.search(r"\b(what can you|what do you|how can you|help me|your capabilities|what questions|what can i ask)\b", message_lower):
        return (
            "I can help you with:\n"
            "• Symptoms: fever, cough, cold, chest pain, headache, stomach pain, vomiting, diarrhoea, dizziness, rash, and many more\n"
            "• Diseases: diabetes, hypertension, dengue, malaria, typhoid, asthma, COVID, anemia, thyroid, and more\n"
            "• Lab results: hemoglobin, blood sugar, creatinine, cholesterol, WBC, platelets, and other values\n"
            "• Medicines: what they do, how to take them, and safe-use instructions\n"
            "• Diet and lifestyle advice for your specific condition\n"
            "• When to see a doctor urgently\n"
            "Just type your question or describe your symptoms!"
        )

    # ── Affirmative short answers (yes/no during follow-up interview) ─────────
    yes_pattern = r"^(yes|yeah|yep|yup|correct|that.?s right|sure|absolutely|definitely|i do|i have|i am|it is|it does|haan|ha)[\s.!]*$"
    no_pattern = r"^(no|nope|nah|not really|don.t|doesn.t|haven.t|i don.t|i haven.t|not at all|none|never|nahi|na)[\s.!]*$"
    if re.match(yes_pattern, message_lower):
        return "Got it, thank you for confirming. Please tell me more about how it feels or when it started."
    if re.match(no_pattern, message_lower):
        return "Understood. That's helpful information. Is there anything else about your symptoms I should know?"

    # ── Duration answers ──────────────────────────────────────────────────────
    duration_pattern = r"\b(\d+\s*(day|days|week|weeks|month|months|hour|hours|since|ago|yesterday|morning|night))\b"
    if re.search(duration_pattern, message_lower) and not current_condition:
        return (
            "Thank you. Duration is important for understanding your condition. "
            "Symptoms lasting more than 3 days should be evaluated by a doctor. "
            "Can you also describe the severity — mild, moderate, or severe?"
        )

    # ── Better/worse responses ────────────────────────────────────────────────
    if re.search(r"\b(feeling better|getting better|improved|improving|recovering|feel good now)\b", message_lower):
        return (
            "That's encouraging! Continue your prescribed treatment and complete the full course of any medicines. "
            "If symptoms return or worsen, consult your doctor again. Stay hydrated and get adequate rest."
        )
    if re.search(r"\b(getting worse|feel worse|worsening|not improving|no improvement|still sick|still have|not getting better)\b", message_lower):
        return (
            "I'm sorry to hear that. Worsening symptoms after 2-3 days of treatment need medical attention. "
            "Please contact your doctor or visit a clinic — they may need to adjust your treatment. "
            "Note down when it started, what makes it worse, and any other new symptoms."
        )

    # ══════════════════════════════════════════════════════════════════════════
    # CONDITION-SPECIFIC DETAILED RESPONSES
    # ══════════════════════════════════════════════════════════════════════════

    # ── FEVER ─────────────────────────────────────────────────────────────────
    if current_condition == "fever" or re.search(r"\b(fever|temperature|febrile|\d{3}°?\s*[fF]|\d{2,3}\s*degree)\b", message_lower):
        if any(temp in message_lower for temp in ["103", "104", "105", "106"]):
            return (
                "A fever above 102°F (39°C) is high and needs attention. Take prescribed paracetamol (500mg for adults), "
                "sponge forehead with lukewarm water, and drink lots of fluids. "
                "See a doctor immediately if fever exceeds 104°F, lasts over 2 days, or is accompanied by "
                "rash, stiff neck, severe headache, or difficulty breathing."
            )
        if any(temp in message_lower for temp in ["99", "100", "101"]):
            return (
                "A mild fever (99-101°F) can often be managed at home. Drink plenty of fluids, "
                "rest, and monitor temperature every 4-6 hours. Take paracetamol as per the dose on the label. "
                "See a doctor if it rises above 102°F, lasts more than 3 days, or you develop new symptoms."
            )
        if re.search(r"\b(chills|shivering|rigor|sweating)\b", message_lower):
            return (
                "Chills and sweating with fever can indicate an infection — sometimes malaria or dengue. "
                "Keep yourself warm during chills, sip warm fluids, and take your prescribed fever medication. "
                "If it's a cyclic pattern (every 48-72 hours), see a doctor and get a blood test."
            )
        if re.search(r"\b(child|baby|infant|toddler|kid|son|daughter)\b", message_lower):
            return (
                "For children: any fever above 100.4°F (38°C) in infants under 3 months needs IMMEDIATE doctor attention. "
                "For older children, give paracetamol syrup at the right weight-based dose, offer fluids, and dress lightly. "
                "See a doctor if the child has a rash, stiff neck, fits, is very drowsy, or won't drink for 8+ hours."
            )
        if re.search(r"\b(3 day|three day|4 day|four day|5 day|week|persist|won.t go)\b", message_lower):
            return (
                "Fever lasting more than 3 days needs a doctor's evaluation. You may need blood tests to check for "
                "dengue, malaria, typhoid, or other infections. Do not take antibiotics without a prescription. "
                "Stay hydrated and continue monitoring temperature until you see a doctor."
            )
        return (
            "Monitor your temperature every 4-6 hours. Stay well-hydrated (water, ORS, coconut water), rest in a cool room, "
            "and take prescribed paracetamol only (avoid aspirin unless prescribed). "
            "See a doctor if fever persists over 3 days, exceeds 104°F, or other symptoms appear."
        )

    # ── COLD / FLU / RUNNING NOSE ─────────────────────────────────────────────
    if current_condition == "cold_flu" or re.search(r"\b(cold|flu|runny nose|blocked nose|stuffy nose|sneezing|sore throat|body ache|influenza)\b", message_lower):
        return (
            "Common cold/flu: rest as much as possible and drink plenty of warm fluids. "
            "Steam inhalation 2-3 times daily helps relieve nasal congestion. "
            "Honey with warm water or ginger tea soothes the throat. "
            "Paracetamol helps with body aches and fever. Saline nasal drops can clear the nose. "
            "See a doctor if symptoms worsen after 5-7 days, fever is high, or you have difficulty breathing."
        )

    # ── SORE THROAT ───────────────────────────────────────────────────────────
    if current_condition == "sore_throat" or re.search(r"\b(sore throat|throat pain|throat ache|tonsil|swallowing|strep)\b", message_lower):
        return (
            "For sore throat: gargle with warm salt water (1/4 tsp salt in 1 cup warm water) 3-4 times a day. "
            "Drink warm liquids — ginger tea, turmeric milk, or warm water. Avoid cold drinks and ice cream. "
            "Paracetamol helps with pain. If throat is very red with white patches, fever, or swollen glands, "
            "see a doctor — you may have strep throat needing antibiotics."
        )

    # ── DENGUE ────────────────────────────────────────────────────────────────
    if current_condition == "dengue" or re.search(r"\b(dengue|ns1|platelet.{0,10}(low|drop|falling)|aedes|breakbone)\b", message_lower):
        return (
            "⚠️ Dengue fever is serious and needs medical monitoring.\n"
            "Key warning signs needing IMMEDIATE hospital visit:\n"
            "• Platelet count below 1 lakh (100,000)\n"
            "• Bleeding from gums, nose, or in stool\n"
            "• Severe abdominal pain, persistent vomiting\n"
            "• Difficulty breathing or restlessness\n\n"
            "Home care: drink plenty of fluids (ORS, coconut water, papaya leaf juice). "
            "Take only paracetamol for fever — NEVER aspirin or ibuprofen (they increase bleeding risk). "
            "Get platelet count checked daily as advised by your doctor."
        )

    # ── MALARIA ───────────────────────────────────────────────────────────────
    if current_condition == "malaria" or re.search(r"\b(malaria|plasmodium|cyclic fever|chills fever pattern)\b", message_lower):
        return (
            "Malaria causes cyclic fever (every 48-72 hours) with chills and sweating. "
            "It needs DIAGNOSIS first: blood smear test or rapid antigen test. "
            "Do NOT self-treat — malaria needs specific prescription medicines (chloroquine or artemisinin combination). "
            "While waiting for results: stay hydrated, take paracetamol for fever, use mosquito nets. "
            "Seek medical care urgently if there is confusion, seizures, or severe weakness."
        )

    # ── TYPHOID ───────────────────────────────────────────────────────────────
    if current_condition == "typhoid" or re.search(r"\b(typhoid|enteric fever|widal|salmonella typhi)\b", message_lower):
        return (
            "Typhoid requires antibiotic treatment prescribed by a doctor (usually ciprofloxacin or azithromycin). "
            "Diet during typhoid: easy-to-digest foods — dal, khichdi, curd, boiled vegetables, bananas. "
            "Avoid raw vegetables, spicy or heavy foods, and outside food. "
            "Stay hydrated. Rest completely. Take the FULL antibiotic course. "
            "Stool and urine hygiene is important to prevent spread."
        )

    # ── COVID ─────────────────────────────────────────────────────────────────
    if current_condition == "covid" or re.search(r"\b(covid|corona|covid.19|loss.{0,10}(smell|taste)|long covid)\b", message_lower):
        return (
            "For COVID-19: isolate at home if test positive and symptoms are mild. "
            "Monitor oxygen levels with a pulse oximeter — seek help immediately if SpO2 drops below 94%. "
            "Take paracetamol for fever and body ache. Stay well-hydrated. Rest completely. "
            "Lie on your stomach (prone position) if you feel breathless — this improves oxygen levels. "
            "Contact a doctor if breath shortness worsens, persistent high fever, or severe chest pain. "
            "Loss of smell/taste can last weeks — this usually recovers with time."
        )

    # ── ASTHMA ────────────────────────────────────────────────────────────────
    if current_condition == "asthma" or re.search(r"\b(asthma|inhaler|wheez|bronch|tight chest.{0,10}breath)\b", message_lower):
        return (
            "For an asthma attack: sit upright, use your rescue inhaler (salbutamol/blue inhaler) immediately, "
            "1-2 puffs every 20 minutes for up to 1 hour. Breathe slowly and stay calm. "
            "If no relief in 20 minutes, go to emergency.\n"
            "Daily management: take preventer inhaler as prescribed even when feeling fine. "
            "Identify and avoid triggers: dust, smoke, pollen, cold air, exercise, pets. "
            "Keep your inhaler with you always."
        )

    # ── HYPERTENSION ─────────────────────────────────────────────────────────
    if current_condition == "hypertension" or re.search(r"\b(blood pressure|bp|high bp|hypertension|\d{3}/\d{2,3})\b", message_lower):
        if re.search(r"\b(headache|dizzy|dizziness|blurred vision|vision|nosebleed)\b", message_lower):
            return (
                "Headache, dizziness, blurred vision, or nosebleed with high blood pressure can be warning signs of a "
                "hypertensive crisis. Sit down immediately, rest, and check your BP. "
                "If it reads above 180/120 mmHg, seek emergency care without delay. "
                "Do not lie down — sitting upright is better."
            )
        if re.search(r"\b(diet|food|eat|salt|sodium)\b", message_lower):
            return (
                "For blood pressure control: reduce salt to under 5g/day, avoid pickles, papads, processed and packaged foods. "
                "Follow the DASH diet: fruits, vegetables, whole grains, low-fat dairy. "
                "Limit alcohol, avoid smoking, reduce stress, and exercise regularly. "
                "Even a 5-10 point drop in BP is achievable through diet changes alone."
            )
        if re.search(r"\b(medicine|medication|tablet|drug|forgot|missed dose)\b", message_lower):
            return (
                "Take your BP medication at the same time every day. If you miss a dose, take it as soon as you "
                "remember — skip it if it is almost time for the next dose. Never double dose. "
                "Do not stop BP medication without doctor advice — even if you feel well, the medicine is working."
            )
        return (
            "Monitor blood pressure daily at the same time (morning, before food). Normal is below 120/80 mmHg. "
            "Reduce salt, manage stress, walk 30 min daily, avoid smoking and alcohol, "
            "and take medications consistently. See your doctor every 3 months."
        )

    # ── COUGH ─────────────────────────────────────────────────────────────────
    if current_condition == "cough" or re.search(r"\b(cough(ing)?|I am coughing|dry cough|wet cough|phlegm|mucus)\b", message_lower):
        if re.search(r"\b(blood|haemoptysis|hemoptysis|blood.{0,10}cough)\b", message_lower):
            return (
                "🩸 Coughing up blood requires immediate medical evaluation. "
                "Please visit a doctor or hospital emergency TODAY — do not ignore this."
            )
        if re.search(r"\b(dry|tickle|irritating|no phlegm|no mucus|scratch)\b", message_lower):
            return (
                "A dry cough can be soothed with warm water, honey with ginger tea (1 tsp honey + juice of half a lemon), "
                "and steam inhalation. Avoid cold, dusty, or smoky environments. "
                "If it lasts beyond 2 weeks, see a doctor to rule out asthma, acid reflux, or infection."
            )
        if re.search(r"\b(green|yellow|thick|phlegm|mucus|productive|colou?r)\b", message_lower):
            return (
                "Coloured or thick phlegm often indicates a bacterial infection requiring antibiotics. "
                "See a doctor. In the meantime, stay hydrated, try steam inhalation, and avoid cough suppressants "
                "without a diagnosis — a productive cough is clearing infection."
            )
        if re.search(r"\b(3 week|three week|month|chronic|persistent|ongoing)\b", message_lower):
            return (
                "A cough lasting more than 3 weeks needs medical investigation. Possible causes include: "
                "TB (tuberculosis), asthma, acid reflux, or post-nasal drip. "
                "Please see a doctor and get a chest X-ray if advised. Do not ignore a chronic cough."
            )
        return (
            "Stay hydrated and try steam inhalation twice daily. Avoid cold drinks and dairy. "
            "Honey with warm water or tulsi-ginger tea can soothe the throat. "
            "See a doctor if cough lasts more than 3 weeks, worsens, produces blood, or you have fever."
        )

    # ── RESPIRATORY ───────────────────────────────────────────────────────────
    if current_condition == "respiratory" or re.search(r"\b(short.{0,5}breath|breathless|breathing.{0,10}(hard|difficult|problem)|can.t breathe)\b", message_lower):
        if re.search(r"\b(rest|resting|sitting|at rest|lying|even now)\b", message_lower):
            return (
                "⚠️ Shortness of breath even at rest is a serious red flag. "
                "Sit upright, stay calm, and call for emergency help (108) immediately. "
                "Do not drive yourself or be alone. Check your oxygen level if you have a pulse oximeter."
            )
        return (
            "Difficulty breathing should be evaluated by a healthcare provider. "
            "Sit upright, take slow deep breaths, avoid physical exertion, and seek help if it worsens. "
            "If SpO2 (oxygen level) drops below 94% on a pulse oximeter, go to hospital immediately."
        )

    # ── CHEST PAIN ────────────────────────────────────────────────────────────
    if current_condition == "chest_pain" or re.search(r"\b(chest.{0,10}(pain|tight|heavy|pressure|discomfort))\b", message_lower):
        if re.search(r"\b(arm|jaw|shoulder|neck|left side|radiating|sweating|nausea|cold sweat)\b", message_lower):
            return (
                "🚨 Chest pain spreading to arm, jaw, or shoulder — especially with sweating or nausea — may indicate a heart attack. "
                "Call emergency services (108 / 112) IMMEDIATELY. Chew one aspirin (325mg) if available and not allergic. "
                "Sit still, loosen clothing — do not drive yourself to hospital."
            )
        if re.search(r"\b(breathing|deep breath|inhale|worse.{0,10}breath)\b", message_lower):
            return (
                "Chest pain that worsens with deep breathing may indicate pleurisy, costochondritis, or a lung issue. "
                "This needs medical evaluation today. Avoid physical exertion."
            )
        if re.search(r"\b(burning|acid|after eat|after meal|lying down|heartburn)\b", message_lower):
            return (
                "Burning chest pain that worsens after meals or when lying down is likely acid reflux (GERD). "
                "Try antacids after meals, eat smaller portions, and avoid lying down within 2 hours of eating. "
                "Avoid spicy, fatty foods and coffee. See a doctor if it persists."
            )
        return (
            "Any new or persistent chest pain should be evaluated by a doctor to rule out cardiac causes. "
            "Note what triggers it, how long it lasts, and its severity (1-10). "
            "If pain is severe, spreading, or comes with sweating or breathlessness, seek emergency help immediately."
        )

    # ── PALPITATIONS ─────────────────────────────────────────────────────────
    if current_condition == "palpitations" or re.search(r"\b(palpitation|heart.{0,10}(racing|pound|flutter|skip)|irregular.{0,10}heartbeat|fast.{0,10}heart)\b", message_lower):
        return (
            "Occasional palpitations (fluttering, rapid, or skipped beats) can be caused by stress, "
            "caffeine, dehydration, anaemia, or thyroid problems. "
            "Try: slow deep breathing (4-4-4 count), reduce caffeine and alcohol, stay hydrated. "
            "See a doctor if palpitations are frequent, last more than a few minutes, come with "
            "chest pain, dizziness, or fainting — you may need an ECG."
        )

    # ── DIZZINESS ─────────────────────────────────────────────────────────────
    if current_condition == "dizziness" or re.search(r"\b(dizzy|dizziness|vertigo|lightheaded|spinning|balance.{0,10}(problem|issue))\b", message_lower):
        return (
            "Dizziness can be caused by: low blood pressure (especially on standing up), dehydration, "
            "anaemia, inner ear issues (vertigo), low blood sugar, or side effects of medicines. "
            "Sit or lie down when dizzy to prevent falls. Drink water. "
            "If dizziness is sudden, severe, with vomiting, or comes with weakness/slurred speech, "
            "seek emergency help — it could be a stroke."
        )

    # ── FAINTING ─────────────────────────────────────────────────────────────
    if current_condition == "fainting" or re.search(r"\b(faint|passed out|blackout|lose.{0,5}consciousness|collapse)\b", message_lower):
        return (
            "Fainting (syncope) can be caused by dehydration, low blood pressure, low blood sugar, or heart rhythm issues. "
            "After fainting: lie flat with legs elevated, loosen clothing, and check for breathing. "
            "Do not give anything by mouth until fully awake. "
            "Anyone who has fainted should be evaluated by a doctor — especially if chest pain, injury, or no clear cause."
        )

    # ── DIABETES ─────────────────────────────────────────────────────────────
    if current_condition == "diabetes" or re.search(r"\b(diabetes|blood.{0,5}sugar|glucose|insulin|diabetic|hba1c|sugar level)\b", message_lower):
        if re.search(r"\b(low|hypo|shaky|sweaty|dizzy|confused|sugar low|feeling weak.{0,20}sugar)\b", message_lower):
            return (
                "Low blood sugar (hypoglycaemia) needs fast treatment: immediately eat 2-3 glucose tablets, "
                "half a cup of fruit juice, or 3 teaspoons of sugar in water. Recheck in 15 minutes. "
                "If unconscious, call emergency services (108) immediately — do not give anything by mouth."
            )
        if re.search(r"\b(300|400|500|600|very high|too high|hyperglycemia|sugar very high)\b", message_lower):
            return (
                "Blood sugar above 300 mg/dL needs prompt attention. Drink plain water and avoid eating. "
                "Take your prescribed insulin/medication and contact your doctor today. "
                "Watch for excessive thirst, vomiting, fruity-smelling breath, or confusion — "
                "these may indicate a dangerous condition called DKA requiring hospital care."
            )
        if re.search(r"\b(diet|food|eat|sugar|carb|sweet|rice|roti|what.{0,10}eat)\b", message_lower):
            return (
                "Diabetic diet tips:\n"
                "• Choose whole grains: brown rice, oats, millet, jowar — avoid white rice and maida\n"
                "• Eat plenty of non-starchy vegetables (bhindi, brinjal, lauki, bitter gourd)\n"
                "• Include lean protein: pulses, eggs, fish, low-fat dairy\n"
                "• Limit fruit portions and avoid mango, grapes, banana in large amounts\n"
                "• Avoid sugar, fried foods, bakery items, and sugary drinks\n"
                "• Eat small frequent meals every 3-4 hours to keep sugar stable"
            )
        return (
            "Monitor fasting blood sugar (target: 70-130 mg/dL) and post-meal (target: below 180 mg/dL). "
            "Take medications as prescribed, walk 30 minutes daily, and follow a low-sugar high-fibre diet. "
            "Get HbA1c tested every 3 months. Watch your feet for wounds and get annual eye checks."
        )

    # ── HEADACHE ─────────────────────────────────────────────────────────────
    if current_condition == "headache" or re.search(r"\b(headache|head.{0,5}pain|head.{0,5}ache|migraine|throbbing.{0,10}head)\b", message_lower):
        if re.search(r"\b(sudden|worst|thunderclap|stiff.{0,5}neck|light.{0,5}sensitive|photophobia|fever.{0,10}headache)\b", message_lower):
            return (
                "A sudden severe headache — 'worst of your life' — or headache with stiff neck, fever, and light sensitivity "
                "can indicate meningitis or a brain bleed. Seek emergency care IMMEDIATELY."
            )
        if re.search(r"\b(migraine|one side|throbbing|aura|visual|zigzag|light|sound)\b", message_lower):
            return (
                "Migraines: at the first sign, take your prescribed medicine and rest in a quiet, dark, cool room. "
                "Apply a cold compress to the forehead or neck. Stay hydrated. "
                "Common triggers: stress, bright light, certain foods (cheese, chocolate, wine), dehydration, poor sleep. "
                "Keep a headache diary to identify your personal triggers."
            )
        if re.search(r"\b(stress|tension|neck|shoulder|tight)\b", message_lower):
            return (
                "Tension headaches (dull ache around the head) are usually triggered by stress, screen time, or poor posture. "
                "Try: rest, neck stretches, paracetamol, warm compress on neck and shoulders, and reducing screen time. "
                "Regular sleep, hydration, and stress management prevent recurrence."
            )
        return (
            "Rest in a quiet, dark room. Stay well-hydrated. Apply a cold or warm compress to the forehead. "
            "Take paracetamol if needed. If headaches are frequent (more than 3/week), worsening over time, "
            "or come with vomiting, vision changes, or weakness, see a doctor promptly."
        )

    # ── ANEMIA ────────────────────────────────────────────────────────────────
    if current_condition == "anemia" or re.search(r"\b(anemia|anaemia|low.{0,10}hb|hemoglobin.{0,10}low|iron.{0,10}deficien|pale|pallor)\b", message_lower):
        if re.search(r"\b(iron|ferritin|supplement|tablet)\b", message_lower):
            return (
                "Iron tablets: take on an empty stomach with a glass of lemon juice or orange juice (Vitamin C increases absorption). "
                "Avoid tea, coffee, milk, calcium, or antacids within 2 hours of taking iron. "
                "Black stools are normal while on iron supplements. Take for at least 3 months. "
                "Eat iron-rich foods daily: spinach, methi, lentils, dates, dried apricots, red meat."
            )
        return (
            "For anaemia: eat iron-rich foods (leafy greens, lentils, eggs, lean meat, dates, pumpkin seeds), "
            "take prescribed iron or B12 supplements consistently, and attend follow-up blood tests. "
            "Avoid tea/coffee with meals — they block iron absorption. "
            "Fatigue and breathlessness should improve as haemoglobin normalises over 4-8 weeks."
        )

    # ── INFECTION ────────────────────────────────────────────────────────────
    if current_condition == "infection" or re.search(r"\b(infection|pus|wound.{0,10}infect|abscess|red.{0,10}swollen)\b", message_lower):
        if re.search(r"\b(antibiotic|amoxicillin|azithromycin|ciprofloxacin|course)\b", message_lower):
            return (
                "Complete the FULL antibiotic course — never stop early even if you feel better. "
                "Stopping early can cause antibiotic resistance and relapse. "
                "Take antibiotics at the prescribed times, finish all tablets, and return to your doctor if no improvement in 3-5 days."
            )
        return (
            "Take prescribed antibiotics — full course. Rest, stay hydrated, and eat nutritious food. "
            "For wound infections: keep clean, change dressing as advised, watch for spreading redness or pus. "
            "Return to your doctor if no improvement in 3-5 days or if fever rises."
        )

    # ── VOMITING / NAUSEA ─────────────────────────────────────────────────────
    if current_condition == "vomiting" or re.search(r"\b(vomit|vomiting|nausea|throwing up|puke|feeling sick)\b", message_lower):
        return (
            "For nausea/vomiting: take small sips of ORS (oral rehydration solution) or coconut water every 15 minutes. "
            "Avoid solid food until vomiting stops for 2+ hours, then start with plain crackers or plain rice. "
            "Ginger tea, jeera water, or peppermint can ease nausea. "
            "See a doctor if: vomiting lasts more than 24 hours, there is blood in vomit, severe abdominal pain, "
            "you can't keep fluids down, or you feel extremely weak."
        )

    # ── DIARRHOEA ─────────────────────────────────────────────────────────────
    if current_condition == "diarrhea" or re.search(r"\b(diarr?h|loose.{0,5}(stool|motion)|runny.{0,5}stool|watery.{0,5}stool|frequent.{0,5}stool)\b", message_lower):
        return (
            "For diarrhoea: drink ORS (oral rehydration solution) regularly — ½ litre after each loose stool. "
            "Coconut water and banana are helpful. Eat: plain rice, banana, toast, curd. "
            "Avoid dairy (except curd), spicy, oily, or raw foods. Wash hands frequently. "
            "See a doctor if: stools contain blood or mucus, diarrhoea lasts more than 3 days, "
            "you feel very weak or dizzy (signs of dehydration), or it affects infants/elderly."
        )

    # ── STOMACH / ABDOMINAL PAIN ──────────────────────────────────────────────
    if current_condition == "stomach" or re.search(r"\b(stomach.{0,10}(pain|ache|cramp)|abdominal.{0,10}pain|belly.{0,10}(pain|ache)|tummy.{0,10}(pain|ache)|indigestion)\b", message_lower):
        if re.search(r"\b(right.{0,10}lower|appendix|sharp.{0,10}right)\b", message_lower):
            return (
                "⚠️ Sharp pain in the lower right abdomen could indicate appendicitis. "
                "This is a medical emergency if it's severe or constant. "
                "Do NOT eat, drink, or take pain medicines — go to hospital immediately."
            )
        return (
            "Mild stomach pain: rest and avoid fatty, spicy, or heavy food. "
            "Try warm water, jeera (cumin) water, or omum (ajwain) with warm water. "
            "Severe, sudden, or persistent abdominal pain — especially lower right side or with fever — "
            "needs medical evaluation: it could be appendicitis, gastritis, kidney stones, or another condition. "
            "Do not ignore persistent abdominal pain."
        )

    # ── ACIDITY / HEARTBURN ───────────────────────────────────────────────────
    if current_condition == "acidity" or re.search(r"\b(acidity|acid.{0,10}reflux|heartburn|gerd|burning.{0,10}(chest|throat|stomach)|gas|bloat|belch)\b", message_lower):
        return (
            "For acidity/heartburn: take an antacid after meals (not on empty stomach). "
            "Eat smaller, more frequent meals. Avoid: spicy, oily, fried food, coffee, alcohol, citrus, and chocolate. "
            "Don't lie down for 2 hours after eating. Elevate the head of your bed slightly. "
            "Lose weight if overweight — it significantly reduces acid reflux. "
            "See a doctor if acidity is frequent (more than twice a week) — you may need prescription medicine."
        )

    # ── CONSTIPATION ──────────────────────────────────────────────────────────
    if current_condition == "constipation" or re.search(r"\b(constipat|no bowel|hard stool|not passing stool|difficult bowel|straining)\b", message_lower):
        return (
            "For constipation: increase water intake (8-10 glasses/day), eat high-fibre foods "
            "(vegetables, fruits, whole grains, pulses), and exercise daily. "
            "Warm water with lemon in the morning helps. Isabgol (psyllium husk) in water before bed can help. "
            "Avoid processed foods, low fibre foods, and holding the urge to go. "
            "If constipation is severe, bloody, or lasts more than 2 weeks, see a doctor."
        )

    # ── SWELLING / OEDEMA ─────────────────────────────────────────────────────
    if current_condition == "swelling" or re.search(r"\b(swelling|swollen|edema|oedema|puffy|puffiness|water.{0,10}retention)\b", message_lower):
        if re.search(r"\b(face|eye|eyelid|lip|tongue|throat|allerg)\b", message_lower):
            return (
                "🚨 Swelling of the face, lips, tongue, or throat is a MEDICAL EMERGENCY called anaphylaxis. "
                "Call 108 immediately. If prescribed, use an epinephrine auto-injector now."
            )
        return (
            "Swelling (oedema) in feet/legs can result from: sitting too long, pregnancy, heart failure, "
            "kidney or liver disease, or venous insufficiency. "
            "Elevate your legs when resting, reduce salt intake, stay hydrated, and avoid prolonged sitting/standing. "
            "New or worsening swelling with breathlessness, chest pain, or weight gain needs urgent medical evaluation."
        )

    # ── JOINT / MUSCLE PAIN ───────────────────────────────────────────────────
    if current_condition == "joint_pain" or re.search(r"\b(joint.{0,10}pain|arthritis|knee.{0,10}pain|body.{0,10}ache|muscle.{0,10}pain|myalgia|elbow|wrist.{0,10}pain)\b", message_lower):
        return (
            "For joint or muscle pain: rest the affected area and apply a cold compress (first 48 hours) then warm compress. "
            "Paracetamol or ibuprofen (after food) helps short-term. Gentle movement is better than complete rest. "
            "Persistent joint pain with swelling, morning stiffness (lasting >30 min), or deformity "
            "should be investigated for arthritis, dengue, or chikungunya. See a doctor."
        )

    # ── BACK PAIN ─────────────────────────────────────────────────────────────
    if re.search(r"\b(back.{0,10}pain|lower.{0,10}back|backache|spine|lumbar|slipped.{0,5}disc|sciatica|neck.{0,10}pain)\b", message_lower):
        return (
            "For most back pain: avoid complete bed rest — gentle movement helps. Apply heat or ice alternately. "
            "Prescribed pain relief helps. Strengthening exercises for the back/core speed recovery. "
            "See a doctor if pain is severe, shoots down the leg (sciatica), follows an injury, or "
            "comes with numbness/weakness in legs or bladder issues."
        )

    # ── SKIN / RASH / ALLERGY ─────────────────────────────────────────────────
    if current_condition == "skin" or current_condition == "allergy" or re.search(r"\b(rash|skin.{0,10}(itch|problem|rash)|hives|allerg|eczema|red.{0,5}spot|red.{0,5}patch)\b", message_lower):
        if re.search(r"\b(face|lip|tongue|throat|allerg|anaphylax)\b", message_lower):
            return (
                "🚨 Rash on face with swelling of lips/throat may indicate anaphylaxis — call 108 immediately."
            )
        return (
            "For skin rashes/itching: avoid scratching — it worsens the rash and can cause infection. "
            "Cool water compresses or calamine lotion relieves itching. "
            "Antihistamine (like cetirizine 10mg once at night) helps for allergic rashes. "
            "See a doctor if rash spreads rapidly, blisters, is painful, has pus, or comes with fever or joint pain."
        )

    # ── EYES ──────────────────────────────────────────────────────────────────
    if current_condition == "ear" or re.search(r"\b(eye.{0,10}(red|pain|itch|water|discharge|pus|pink eye)|conjunctivitis|watery.{0,5}eye|eye.{0,10}infect)\b", message_lower):
        return (
            "For red/watery eyes (conjunctivitis): avoid touching or rubbing them. Rinse with clean water 3-4 times/day. "
            "It is contagious — wash hands frequently, don't share towels or pillows. "
            "Antibiotic eye drops may be needed — see a doctor for prescription. "
            "Sudden loss of vision, severe eye pain, or eye injury needs emergency ophthalmology care."
        )

    # ── EAR ───────────────────────────────────────────────────────────────────
    if current_condition == "ear" or re.search(r"\b(ear.{0,10}(pain|ache|infect|discharge|ringing|block)|earache|tinnitus|hearing.{0,5}(loss|problem))\b", message_lower):
        return (
            "For earache: do not insert anything into the ear canal. A warm compress against the ear can ease pain. "
            "Paracetamol helps with pain. Ear infections often need antibiotic ear drops — see a doctor. "
            "Ringing in the ear (tinnitus) or sudden hearing loss needs medical evaluation as soon as possible."
        )

    # ── SLEEP / FATIGUE ───────────────────────────────────────────────────────
    if re.search(r"\b(sleep|insomnia|can.t sleep|not sleeping|trouble.{0,10}sleep|fatigue|tired|exhausted|weakness)\b", message_lower):
        return (
            "For better sleep: maintain a consistent bedtime routine, avoid screens 1 hour before bed, "
            "limit caffeine after 2 PM, and keep the room dark and cool. Regular exercise improves sleep. "
            "Chronic unexplained fatigue (lasting 2+ weeks) alongside other symptoms should be investigated: "
            "it can signal anaemia, thyroid problems, diabetes, or viral infections. Get a basic blood test."
        )

    # ── MENTAL HEALTH / STRESS ────────────────────────────────────────────────
    if current_condition == "mental_health" or re.search(r"\b(stress|anxiety|anxious|panic|depressed|depression|mental|sad|worry|worried|hopeless|overwhelm)\b", message_lower):
        if re.search(r"\b(suicid|harm.{0,10}myself|self.{0,5}harm|end.{0,10}life|want to die|no point)\b", message_lower):
            return (
                "💙 I'm really sorry you're feeling this way. You deserve support. "
                "Please reach out immediately to iCall (9152987821) or Vandrevala Foundation (1860-2662-345) — "
                "both are free and confidential. Talk to someone you trust. You are not alone."
            )
        return (
            "Mental health is as important as physical health. For stress and anxiety: "
            "try slow deep breathing (breathe in 4 counts, hold 4, breathe out 6). "
            "Regular exercise, social connection, and limiting news/social media all help. "
            "If feelings of sadness, anxiety, or hopelessness persist or affect daily life, "
            "please speak to a doctor or counsellor — effective treatment is available and it's okay to ask for help."
        )

    # ── KIDNEY / URINE ────────────────────────────────────────────────────────
    if current_condition == "kidney" or current_condition == "urinary" or re.search(r"\b(kidney|urin(e|ation)|burning.{0,10}urin|uti|frequent.{0,10}urin|blood.{0,10}urin|kidney.{0,10}stone|creatinine)\b", message_lower):
        if re.search(r"\b(stone|stones|calculi|flank.{0,5}pain|side.{0,5}pain.{0,10}back)\b", message_lower):
            return (
                "Kidney stones cause severe colicky pain from back to lower abdomen. "
                "Drink plenty of water (3-4 litres/day) to help pass small stones. Paracetamol or prescribed pain relief helps. "
                "Large stones causing fever, persistent vomiting, or blockage need hospital evaluation urgently."
            )
        return (
            "Burning/frequent urination may indicate a UTI (urinary tract infection). "
            "Drink plenty of water (8-10 glasses/day). See a doctor for urine test and antibiotics if needed. "
            "Blood in urine, fever with pain, or flank pain (lower back) needs urgent evaluation — "
            "could be kidney infection or stones."
        )

    # ── LIVER / JAUNDICE ──────────────────────────────────────────────────────
    if current_condition == "liver" or re.search(r"\b(liver|jaundice|yellow.{0,10}(skin|eye)|bilirubin|hepatitis|sgpt|sgot)\b", message_lower):
        return (
            "Jaundice (yellowing of skin/eyes) and elevated liver enzymes need prompt medical evaluation. "
            "Causes include: hepatitis A/B/E, biliary obstruction, or other liver disease. "
            "Rest completely, avoid alcohol entirely, eat light easily digestible food (khichdi, curd, fruits), "
            "and stay hydrated with clean water. Follow up with your doctor for repeat liver function tests."
        )

    # ── THYROID ───────────────────────────────────────────────────────────────
    if current_condition == "thyroid" or re.search(r"\b(thyroid|tsh|hypothyroid|hyperthyroid|thyroxine|weight.{0,10}change.{0,10}thyroid)\b", message_lower):
        return (
            "Thyroid conditions are managed with daily medication (thyroxine/eltroxin for hypothyroidism). "
            "Take your tablet first thing in the morning on an empty stomach, 30-45 minutes before food. "
            "Avoid calcium, iron, or antacids within 4 hours. Get TSH tested every 6 months or as advised. "
            "Symptoms like unexplained weight change, fatigue, hair loss, feel cold/hot all the time "
            "— tell your doctor so the dose can be adjusted."
        )

    # ── DENGUE (extra check) ──────────────────────────────────────────────────
    if current_condition == "dengue":
        return (
            "⚠️ Dengue requires close medical monitoring. Warning signs needing IMMEDIATE hospital visit: "
            "platelet below 1 lakh, bleeding (gums, nose, stool), severe abdominal pain, persistent vomiting, "
            "difficulty breathing, or extreme restlessness.\n"
            "Home care: ORS/coconut water every hour, papaya leaf juice may help platelets. "
            "Only paracetamol for fever — NEVER aspirin or ibuprofen. Check platelets daily as directed."
        )

    # ── LAB VALUES / REPORT TERMS ─────────────────────────────────────────────
    lab_pattern = r"\b(hemoglobin|hb|wbc|rbc|platelet|creatinine|urea|bun|uric acid|cholesterol|ldl|hdl|triglyceride|glucose|hba1c|esr|crp|d.dimer|troponin|bilirubin|albumin|sodium|potassium|calcium|report|result|value|reading|level|count|normal.{0,5}range|lab|blood.{0,5}test|cbc|lipid)\b"
    if re.search(lab_pattern, message_lower):
        return (
            "Common normal lab ranges (adult):\n"
            "• Hemoglobin: Men 13–17 g/dL | Women 12–15 g/dL\n"
            "• Fasting blood sugar: 70–100 mg/dL | Post-meal: <140 mg/dL\n"
            "• HbA1c: <5.7% normal | 5.7–6.4% pre-diabetes | ≥6.5% diabetes\n"
            "• Total cholesterol: <200 mg/dL | LDL: <100 mg/dL | HDL: >40 mg/dL (men), >50 (women)\n"
            "• Creatinine: 0.6–1.2 mg/dL | Urea: 7–20 mg/dL\n"
            "• WBC: 4,500–11,000 cells/mcL | Platelets: 1.5–4 lakh/mcL\n"
            "• TSH: 0.4–4.0 mU/L | Bilirubin: <1.2 mg/dL\n"
            "Share your specific value and I'll explain what it means for you."
        )

    # ── EXPLANATION / WHAT IS ─────────────────────────────────────────────────
    if re.search(r"\b(what is|what are|explain|meaning|means|understand|tell me about|define|definition|difference between)\b", message_lower):
        # Try to extract the topic being asked about
        topic_match = re.search(r"what is\s+(.+?)(\?|$)", message_lower)
        if topic_match:
            topic = topic_match.group(1).strip()
            # Check if topic matches any known condition
            for cond, pattern in _CONDITION_PATTERNS.items():
                if re.search(pattern, topic, re.IGNORECASE):
                    # Re-enter with condition set
                    return generate_response(f"I have {topic}", {**context, "current_condition": cond})
        return (
            "I'd be happy to explain that. Please share the specific medical term, value, or reading "
            "from your report — for example: 'What is hemoglobin?', 'What does BP 140/90 mean?', "
            "'What is dengue?', or 'What is creatinine?' and I'll give you a clear plain-language explanation."
        )

    # ── MEDICINE / DOSAGE ─────────────────────────────────────────────────────
    if re.search(r"\b(medicine|medication|tablet|drug|dosage|dose|should i take|can i take|side effect|safe to take)\b", message_lower):
        # Check for specific medicine names
        meds = _extract_medications(user_message)
        if meds:
            tips = []
            for med in meds:
                tip = _MEDICATION_KEYWORDS.get(med)
                if tip:
                    tips.append(f"• {med.title()}: {tip}")
            if tips:
                return "\n".join(tips) + "\n\nAlways follow your doctor's prescription and never self-medicate."
        return (
            "I can give general guidance on common medicines — always follow your doctor's prescription.\n"
            "Key points:\n"
            "• Complete the full course of antibiotics — never stop early\n"
            "• BP and diabetes medicines must be taken every day, even when you feel well\n"
            "• Take paracetamol at the lowest needed dose; avoid in liver disease\n"
            "• Never combine NSAIDs (ibuprofen, diclofenac) with blood thinners without doctor advice\n"
            "Tell me the medicine name and I'll give specific safe-use tips."
        )

    # ── SERIOUS / SHOULD I SEE A DOCTOR ──────────────────────────────────────
    if re.search(r"\b(is this serious|should i see|need a doctor|see a doctor|go to hospital|go to emergency|need emergency|doctor advice|when.{0,10}hospital)\b", message_lower):
        if risk_level.lower() == "high":
            return (
                "⚠️ Based on your report, your risk is HIGH. Yes — please see a doctor today or visit a hospital. "
                "Do not delay. Take your report and list of symptoms with you."
            )
        elif risk_level.lower() == "moderate":
            return (
                "Your risk level is MODERATE. You should see a doctor within the next 1-2 days. "
                "Monitor your symptoms and go to emergency if they worsen quickly — "
                "especially breathlessness, severe chest/abdominal pain, high fever, or confusion."
            )
        else:
            return (
                "Your report shows a LOW risk level. That's reassuring. However, if a symptom is "
                "persistent, spreading, worsening, or causing significant discomfort, a doctor visit is always a good idea. "
                "Trust your instincts — if something doesn't feel right, get it checked."
            )

    # ── PREGNANCY / WOMEN'S HEALTH ────────────────────────────────────────────
    if re.search(r"\b(pregnant|pregnancy|trimester|antenatal|prenatal|period|menstrual|pcod|pcos|gynaecol|gynecol)\b", message_lower):
        return (
            "Pregnancy and women's health require personalised medical care. "
            "Always consult your gynaecologist/obstetrician for medicines, supplements, and diet during pregnancy. "
            "Do not take any medicine during pregnancy without your doctor's approval — even OTC medicines. "
            "For PCOD/PCOS: lifestyle changes (exercise, low-carb diet) alongside medical management are key."
        )

    # ── CHILD / PAEDIATRIC ────────────────────────────────────────────────────
    if re.search(r"\b(child|baby|infant|toddler|kid|children|paediatric|pediatric|newborn)\b", message_lower):
        return (
            "For children's health, always consult a paediatrician. "
            "Signs that need IMMEDIATE attention: fever above 103°F, rapid breathing, blue lips, "
            "not drinking fluids for 8+ hours, unusual drowsiness, rash with fever. "
            "Never give adult medications to children without a doctor's guidance."
        )

    # ── DIET / NUTRITION / LIFESTYLE ─────────────────────────────────────────
    if re.search(r"\b(diet|food|eat|nutrition|drink|water|exercise|walk|lifestyle|weight|obesity|healthy)\b", message_lower):
        return (
            "General healthy lifestyle:\n"
            "• Eat plenty of vegetables, fruits, whole grains, and lean protein\n"
            "• Limit salt, sugar, fried food, and packaged/processed items\n"
            "• Drink 8-10 glasses of water daily\n"
            "• Exercise at least 30 minutes most days (walking is excellent)\n"
            "• Sleep 7-8 hours per night\n"
            "• Avoid smoking and limit alcohol\n"
            "If you have a specific condition (diabetes, BP, kidney disease), ask me for tailored diet advice!"
        )

    # ── NUMBNESS / TINGLING ───────────────────────────────────────────────────
    if current_condition == "numbness" or re.search(r"\b(numb|numb(ness)?|tingling|pins.{0,5}needles|nerve.{0,10}pain|weakness.{0,5}(arm|leg|hand|foot))\b", message_lower):
        return (
            "Numbness and tingling can result from: nerve compression (poor posture), vitamin B12 deficiency, "
            "diabetes (peripheral neuropathy), cervical/lumbar disc issues, or reduced blood flow. "
            "New sudden numbness especially on one side of body with weakness or slurred speech "
            "is a STROKE symptom — call 108 immediately. Otherwise, see a doctor for evaluation."
        )

    # ── BLEEDING ─────────────────────────────────────────────────────────────
    if current_condition == "bleeding" or re.search(r"\b(bleed(ing)?|blood.{0,10}(stool|vomit|urine|cough)|black.{0,10}stool|tarry.{0,5}stool)\b", message_lower):
        return (
            "Any unexplained bleeding — blood in stool, vomit, urine, or cough — needs medical evaluation. "
            "Black/tarry stools can indicate bleeding in the upper digestive tract and require urgent attention. "
            "Do not ignore this — see a doctor today."
        )

    # ── WEIGHT LOSS ───────────────────────────────────────────────────────────
    if current_condition == "weight_loss" or re.search(r"\b(unexplained.{0,10}weight.{0,10}loss|losing.{0,10}weight.{0,10}without|drastic.{0,10}weight)\b", message_lower):
        return (
            "Unexplained weight loss (more than 5% of body weight in 6-12 months without trying) can indicate: "
            "diabetes, thyroid overactivity, TB, cancer, or malabsorption. "
            "Please see a doctor for blood tests and appropriate investigation. Do not ignore this symptom."
        )

    # ── THANK YOU / ACKNOWLEDGEMENT ───────────────────────────────────────────
    if re.search(r"\b(thank|thanks|thank you|ok|okay|understood|got it|alright|fine|noted|good|great)\b", message_lower):
        return (
            "You're welcome! Feel free to ask me anything else about your health or report. "
            "Stay hydrated, take your medications as prescribed, and don't hesitate to see a doctor if anything worries you. 😊"
        )

    # ══════════════════════════════════════════════════════════════════════════
    # SMART FALLBACK — Try to give a useful response based on risk and context
    # ══════════════════════════════════════════════════════════════════════════

    # If message has medical words but didn't match any pattern, try to be helpful
    medical_words = re.search(r"\b(pain|ache|hurt|fever|sick|feel|symptom|problem|issue|suffering|trouble|chronic|acute|sudden|severe|mild|moderate)\b", message_lower)

    if medical_words:
        if risk_level.lower() == "high":
            return (
                f"I noticed you mentioned symptoms. Based on your report, your risk level is HIGH — please describe your symptoms in more detail "
                f"and consider seeing a doctor today. I'm here to help guide you. What exactly are you experiencing?"
            )
        else:
            return (
                "I want to help! Could you describe your symptoms more specifically? For example: "
                "'I have fever since 2 days', 'I have chest pain', 'My knee is swollen', 'What does my sugar level mean?' "
                "The more detail you give me, the better I can assist you."
            )

    # Final catch-all
    if risk_level.lower() == "high":
        return (
            "Based on your report, your risk level is HIGH. Please see a doctor as soon as possible. "
            "I can help you understand your symptoms — please describe how you are feeling and I'll guide you."
        )
    elif risk_level.lower() == "moderate":
        return (
            "Your report shows a MODERATE risk level. Monitor your symptoms and follow up with your doctor. "
            "Can you tell me more about how you are feeling right now?"
        )
    else:
        return (
            "I'm here to help! Ask me about any symptoms (fever, cough, chest pain, diabetes, BP, headache...), "
            "medicines, lab values, diet advice, or when to see a doctor. Just describe what you're experiencing!"
        )



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
