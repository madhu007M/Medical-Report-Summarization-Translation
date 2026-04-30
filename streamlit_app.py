"""AI Medical Report Interpreter — Interactive Streamlit Frontend."""
import os
import uuid
from datetime import datetime
from typing import Optional

import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(
    page_title="MedReport AI",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = False


def css(dark: bool) -> str:
    if dark:
        # ── Dark palette ──
        PAGE_BG      = "#0a0f1e"
        SIDEBAR_BG   = "#0d1526"
        CARD_BG      = "#111c30"
        CARD_BG2     = "#162035"
        BORDER       = "#1e3150"
        TEXT         = "#f0f4ff"
        TEXT_MUTED   = "#7c90b0"
        INPUT_BG     = "#0d1a2e"
        SHADOW       = "rgba(0,0,0,0.5)"
        DIVIDER      = "#1e3150"
        BADGE_BG     = "#1a2c4a"
        HERO_START   = "#1a3a6e"
        HERO_END     = "#0e2550"
    else:
        # ── Light palette ──
        PAGE_BG      = "#f0f4f8"
        SIDEBAR_BG   = "#ffffff"
        CARD_BG      = "#ffffff"
        CARD_BG2     = "#f8faff"
        BORDER       = "#dde3ee"
        TEXT         = "#0d1b2e"
        TEXT_MUTED   = "#5a6a82"
        INPUT_BG     = "#ffffff"
        SHADOW       = "rgba(15,30,60,0.08)"
        DIVIDER      = "#e4e9f2"
        BADGE_BG     = "#eef2ff"
        HERO_START   = "#1a56db"
        HERO_END     = "#1e40af"

    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');

/* ═══════════════════════ KEYFRAME ANIMATIONS ═══════════════════════ */
@keyframes fadeInUp {{
    from {{ opacity: 0; transform: translateY(22px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}
@keyframes fadeIn {{
    from {{ opacity: 0; }}
    to   {{ opacity: 1; }}
}}
@keyframes slideInLeft {{
    from {{ opacity: 0; transform: translateX(-20px); }}
    to   {{ opacity: 1; transform: translateX(0); }}
}}
@keyframes slideInRight {{
    from {{ opacity: 0; transform: translateX(20px); }}
    to   {{ opacity: 1; transform: translateX(0); }}
}}
@keyframes scaleIn {{
    0%   {{ opacity: 0; transform: scale(0.82); }}
    70%  {{ transform: scale(1.04); }}
    100% {{ opacity: 1; transform: scale(1); }}
}}
@keyframes gradientShift {{
    0%   {{ background-position: 0% 50%; }}
    50%  {{ background-position: 100% 50%; }}
    100% {{ background-position: 0% 50%; }}
}}
@keyframes glowPulse {{
    0%,100% {{ box-shadow: 0 0 0 3px rgba(34,197,94,0.25); }}
    50%     {{ box-shadow: 0 0 0 7px rgba(34,197,94,0.08); }}
}}
@keyframes heroBobble {{
    0%,100% {{ transform: scale(1) translateY(0); opacity: 0.04; }}
    50%     {{ transform: scale(1.07) translateY(-8px); opacity: 0.07; }}
}}
@keyframes typingDot {{
    0%,60%,100% {{ transform: translateY(0); opacity: 0.35; }}
    30%         {{ transform: translateY(-7px); opacity: 1; }}
}}
@keyframes riskGlow {{
    0%,100% {{ box-shadow: 0 2px 8px rgba(239,68,68,0.08); }}
    50%     {{ box-shadow: 0 4px 18px rgba(239,68,68,0.18); }}
}}
@keyframes borderSlide {{
    from {{ width: 0%; }}
    to   {{ width: 100%; }}
}}

/* ═══════════════════════ BASE ═══════════════════════ */
html, body, [class*="css"] {{
    font-family: 'Inter', -apple-system, sans-serif !important;
}}
.stApp {{
    background-color: {PAGE_BG} !important;
    color: {TEXT} !important;
}}

/* ═══════════════════════ SIDEBAR ═══════════════════════ */
[data-testid="stSidebar"] {{
    background: {SIDEBAR_BG} !important;
    border-right: 1px solid {BORDER} !important;
}}
[data-testid="stSidebar"] * {{
    color: {TEXT} !important;
}}
[data-testid="stSidebar"] .stCaption {{
    color: {TEXT_MUTED} !important;
}}

/* ═══════════════════════ TABS ═══════════════════════ */
.stTabs [data-baseweb="tab-list"] {{
    background: transparent !important;
    gap: 4px !important;
    border-bottom: 2px solid {BORDER} !important;
    padding-bottom: 0 !important;
}}
.stTabs [data-baseweb="tab"] {{
    background: transparent !important;
    color: {TEXT_MUTED} !important;
    font-weight: 500 !important;
    font-size: 0.9em !important;
    padding: 10px 20px !important;
    border-radius: 8px 8px 0 0 !important;
    border: none !important;
    transition: all 0.2s !important;
}}
.stTabs [aria-selected="true"] {{
    background: {CARD_BG} !important;
    color: #3b82f6 !important;
    font-weight: 600 !important;
    border-top: 3px solid #3b82f6 !important;
}}

/* ═══════════════════════ BUTTONS ═══════════════════════ */
.stButton > button {{
    border-radius: 9px !important;
    font-weight: 600 !important;
    font-size: 0.88em !important;
    padding: 0.52em 1.25em !important;
    transition: all 0.2s ease !important;
    letter-spacing: 0.01em !important;
    position: relative !important;
    overflow: hidden !important;
}}
.stButton > button[kind="primary"] {{
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 50%, #1e40af 100%) !important;
    background-size: 200% 200% !important;
    animation: gradientShift 5s ease infinite !important;
    color: #ffffff !important;
    border: none !important;
    box-shadow: 0 3px 12px rgba(37,99,235,0.38) !important;
}}
.stButton > button[kind="primary"]:hover {{
    box-shadow: 0 6px 22px rgba(37,99,235,0.5) !important;
    transform: translateY(-2px) !important;
}}
.stButton > button[kind="secondary"] {{
    background: {CARD_BG} !important;
    color: {TEXT} !important;
    border: 1.5px solid {BORDER} !important;
}}
.stButton > button[kind="secondary"]:hover {{
    border-color: #3b82f6 !important;
    color: #3b82f6 !important;
    transform: translateY(-1px) !important;
}}
.stButton > button:not([kind]) {{
    background: {CARD_BG} !important;
    color: {TEXT} !important;
    border: 1.5px solid {BORDER} !important;
}}
.stButton > button:not([kind]):hover {{
    border-color: #3b82f6 !important;
    color: #3b82f6 !important;
}}
.stButton > button:disabled {{
    opacity: 0.45 !important;
    transform: none !important;
}}

/* ═══════════════════════ INPUTS ═══════════════════════ */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {{
    background: {INPUT_BG} !important;
    color: {TEXT} !important;
    border: 1.5px solid {BORDER} !important;
    border-radius: 8px !important;
    font-size: 0.9em !important;
    transition: border-color 0.2s !important;
}}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {{
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.15) !important;
}}
.stSelectbox > div > div {{
    background: {INPUT_BG} !important;
    color: {TEXT} !important;
    border: 1.5px solid {BORDER} !important;
    border-radius: 8px !important;
}}
label, .stTextInput label, .stTextArea label, .stSelectbox label {{
    color: {TEXT} !important;
    font-weight: 500 !important;
    font-size: 0.85em !important;
}}

/* ═══════════════════════ FILE UPLOADER ═══════════════════════ */
[data-testid="stFileUploader"] {{
    background: {CARD_BG2} !important;
    border: 2px dashed {BORDER} !important;
    border-radius: 14px !important;
    transition: border-color 0.25s, box-shadow 0.25s, transform 0.2s !important;
    animation: fadeInUp 0.5s ease both;
}}
[data-testid="stFileUploader"]:hover {{
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 4px rgba(59,130,246,0.1) !important;
    transform: translateY(-1px) !important;
}}
[data-testid="stFileUploader"] * {{
    color: {TEXT} !important;
}}

/* ═══════════════════════ EXPANDER ═══════════════════════ */
details summary {{
    background: {CARD_BG2} !important;
    color: {TEXT} !important;
    border: 1.5px solid {BORDER} !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    padding: 10px 16px !important;
}}
details[open] summary {{
    border-bottom-left-radius: 0 !important;
    border-bottom-right-radius: 0 !important;
    border-color: #3b82f6 !important;
}}
details > div {{
    background: {CARD_BG} !important;
    border: 1.5px solid {BORDER} !important;
    border-top: none !important;
    border-radius: 0 0 8px 8px !important;
    padding: 12px !important;
}}

/* ═══════════════════════ ALERTS / MESSAGES ═══════════════════════ */
.stSuccess > div {{ border-radius: 8px !important; }}
.stError   > div {{ border-radius: 8px !important; }}
.stWarning > div {{ border-radius: 8px !important; }}
.stInfo    > div {{ border-radius: 8px !important; }}

/* ═══════════════════════ PROGRESS ═══════════════════════ */
.stProgress > div > div > div > div {{
    background: linear-gradient(90deg, #2563eb, #38bdf8) !important;
    border-radius: 4px !important;
}}

/* ═══════════════════════ SPINNER ═══════════════════════ */
.stSpinner > div {{ border-top-color: #3b82f6 !important; }}

/* ═══════════════════════ DATAFRAME ═══════════════════════ */
.stDataFrame {{ border-radius: 10px !important; overflow: hidden !important; }}

/* ═══════════════════════ CHAT ═══════════════════════ */
.stChatMessage {{
    background: {CARD_BG} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 14px !important;
    animation: fadeInUp 0.35s ease both;
    transition: box-shadow 0.2s;
}}
.stChatMessage:hover {{
    box-shadow: 0 4px 16px {SHADOW} !important;
}}
[data-testid="stChatMessage"][data-message-author-role="user"] {{
    animation: slideInRight 0.35s ease both;
}}
[data-testid="stChatMessage"][data-message-author-role="assistant"] {{
    animation: slideInLeft 0.35s ease both;
}}

/* Chat header */
.chat-header {{
    background: linear-gradient(135deg, {HERO_START} 0%, {HERO_END} 100%);
    background-size: 200% 200%;
    animation: gradientShift 10s ease infinite;
    border-radius: 14px;
    padding: 20px 24px;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 16px;
    box-shadow: 0 4px 18px rgba(30,64,175,0.22);
}}
.chat-header-avatar {{
    font-size: 2.4em;
    background: rgba(255,255,255,0.12);
    border-radius: 50%;
    width: 56px; height: 56px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
    animation: scaleIn 0.6s ease both;
}}
.chat-header-title {{
    font-size: 1.1em;
    font-weight: 700;
    color: #ffffff;
    margin: 0 0 3px 0;
    letter-spacing: -0.01em;
}}
.chat-header-sub {{
    font-size: 0.82em;
    color: rgba(255,255,255,0.72);
    margin: 0;
    font-weight: 400;
}}
.chat-header-badge {{
    margin-left: auto;
    background: rgba(255,255,255,0.15);
    border: 1px solid rgba(255,255,255,0.25);
    border-radius: 20px;
    padding: 5px 14px;
    font-size: 0.78em;
    color: #ffffff;
    font-weight: 600;
    flex-shrink: 0;
}}

/* Typing indicator */
.typing-indicator {{
    display: flex;
    align-items: center;
    gap: 5px;
    padding: 10px 16px;
    background: {CARD_BG};
    border: 1px solid {BORDER};
    border-radius: 10px;
    width: fit-content;
    margin: 4px 0;
    animation: fadeIn 0.3s ease;
}}
.typing-indicator .tdot {{
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #3b82f6;
    animation: typingDot 1.3s ease-in-out infinite;
}}
.typing-indicator .tdot:nth-child(2) {{ animation-delay: 0.18s; }}
.typing-indicator .tdot:nth-child(3) {{ animation-delay: 0.36s; }}

/* Chat disclaimer */
.chat-disclaimer {{
    font-size: 0.78em;
    color: {TEXT_MUTED};
    background: {CARD_BG2};
    border: 1px solid {BORDER};
    border-left: 3px solid #f59e0b;
    border-radius: 8px;
    padding: 8px 14px;
    margin: 8px 0 14px 0;
}}

/* ═══════════════════════ CUSTOM COMPONENTS ═══════════════════════ */

/* Hero banner */
.hero {{
    background: linear-gradient(135deg, {HERO_START} 0%, #1e3a8a 45%, {HERO_END} 100%);
    background-size: 220% 220%;
    animation: gradientShift 9s ease infinite;
    border-radius: 18px;
    padding: 36px 40px;
    margin-bottom: 10px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 8px 32px rgba(30,64,175,0.28);
}}
.hero::before {{
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 220px; height: 220px;
    background: rgba(255,255,255,0.06);
    border-radius: 50%;
    animation: heroBobble 7s ease-in-out infinite;
}}
.hero::after {{
    content: '';
    position: absolute;
    bottom: -70px; left: 18%;
    width: 300px; height: 300px;
    background: rgba(255,255,255,0.04);
    border-radius: 50%;
    animation: heroBobble 11s ease-in-out infinite reverse;
}}
.hero-title {{
    font-size: 1.85em;
    font-weight: 800;
    color: #ffffff;
    margin: 0 0 8px 0;
    letter-spacing: -0.025em;
    text-shadow: 0 2px 12px rgba(0,0,0,0.2);
    animation: fadeInUp 0.7s ease both;
}}
.hero-sub {{
    font-size: 0.97em;
    color: rgba(255,255,255,0.78);
    margin: 0;
    font-weight: 400;
    letter-spacing: 0.01em;
    animation: fadeInUp 0.9s ease both;
}}

/* Cards */
.card {{
    background: {CARD_BG};
    border: 1px solid {BORDER};
    border-radius: 14px;
    padding: 20px 22px;
    margin: 8px 0;
    box-shadow: 0 2px 8px {SHADOW};
    transition: box-shadow 0.25s, transform 0.2s;
    animation: fadeInUp 0.45s ease both;
}}
.card:hover {{
    box-shadow: 0 8px 28px {SHADOW};
    transform: translateY(-2px);
}}
.card-title {{
    font-size: 1em;
    font-weight: 600;
    color: {TEXT};
    margin: 0 0 4px 0;
}}
.card-sub {{
    font-size: 0.83em;
    color: {TEXT_MUTED};
}}

/* Metric cards */
.metric-grid {{ display: flex; gap: 14px; margin: 14px 0; flex-wrap: wrap; }}
.metric {{
    flex: 1;
    min-width: 100px;
    background: {CARD_BG};
    border: 1px solid {BORDER};
    border-radius: 14px;
    padding: 20px 16px;
    text-align: center;
    box-shadow: 0 2px 8px {SHADOW};
    transition: box-shadow 0.2s, transform 0.18s;
    animation: scaleIn 0.5s ease both;
}}
.metric:hover {{
    transform: translateY(-3px);
    box-shadow: 0 8px 24px {SHADOW};
}}
.metric-val {{
    font-size: 2em;
    font-weight: 800;
    line-height: 1;
    letter-spacing: -0.03em;
}}
.metric-lbl {{
    font-size: 0.78em;
    font-weight: 500;
    color: {TEXT_MUTED};
    margin-top: 5px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}}

/* Risk banners */
.risk-high {{
    background: linear-gradient(135deg, #fff1f2 0%, #ffe4e6 100%);
    border: 1px solid #fca5a5;
    border-left: 5px solid #ef4444;
    border-radius: 14px;
    padding: 22px 26px;
    margin: 14px 0;
    display: flex; align-items: center; gap: 18px;
    animation: fadeInUp 0.5s ease both, riskGlow 3s ease-in-out infinite 0.6s;
}}
.risk-moderate {{
    background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
    border: 1px solid #fcd34d;
    border-left: 5px solid #f59e0b;
    border-radius: 14px;
    padding: 22px 26px;
    margin: 14px 0;
    display: flex; align-items: center; gap: 18px;
    animation: fadeInUp 0.5s ease both;
}}
.risk-low {{
    background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
    border: 1px solid #86efac;
    border-left: 5px solid #22c55e;
    border-radius: 14px;
    padding: 22px 26px;
    margin: 14px 0;
    display: flex; align-items: center; gap: 18px;
    animation: fadeInUp 0.5s ease both;
}}
.risk-icon {{ font-size: 2.6em; animation: scaleIn 0.6s ease both; }}
.risk-text-level {{
    font-size: 1.4em;
    font-weight: 800;
    letter-spacing: -0.02em;
}}
.risk-text-score {{
    font-size: 0.88em;
    color: {TEXT_MUTED};
    margin-top: 2px;
}}

/* Step progress */
.steps {{
    display: flex;
    align-items: flex-start;
    justify-content: center;
    padding: 16px 0 4px 0;
    gap: 0;
}}
.step {{
    display: flex;
    flex-direction: column;
    align-items: center;
    flex: 1;
    max-width: 160px;
}}
.step-line {{
    flex: 1;
    height: 2px;
    margin-top: 20px;
    transition: background 0.4s;
}}
.step-line.done {{ background: #22c55e; }}
.step-line.pending {{ background: {BORDER}; }}
.step-num {{
    width: 42px; height: 42px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-weight: 700; font-size: 1em;
    transition: all 0.3s;
    position: relative; z-index: 1;
}}
.step-num.done    {{ background: #22c55e; color: #fff; box-shadow: 0 0 0 4px rgba(34,197,94,0.2); }}
.step-num.active  {{ background: #2563eb; color: #fff; box-shadow: 0 0 0 4px rgba(37,99,235,0.25); animation: stepPulse 1.8s ease infinite; }}
.step-num.pending {{ background: {CARD_BG2}; color: {TEXT_MUTED}; border: 2px solid {BORDER}; }}
.step-lbl {{
    font-size: 0.75em;
    font-weight: 600;
    color: {TEXT_MUTED};
    margin-top: 7px;
    text-align: center;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}}
.step-lbl.active {{ color: #2563eb; }}
.step-lbl.done   {{ color: #22c55e; }}
@keyframes stepPulse {{
    0%,100% {{ box-shadow: 0 0 0 4px rgba(37,99,235,0.2); }}
    50%      {{ box-shadow: 0 0 0 8px rgba(37,99,235,0.1); }}
}}

/* Status dot */
.dot-online  {{ display:inline-block; width:9px; height:9px; border-radius:50%; background:#22c55e; margin-right:7px; animation: glowPulse 2s ease-in-out infinite; }}
.dot-offline {{ display:inline-block; width:9px; height:9px; border-radius:50%; background:#ef4444; margin-right:7px; }}
.status-text {{ font-size:0.84em; font-weight:600; color:{TEXT}; vertical-align:middle; }}

/* Section header */
.sec {{
    font-size: 1.05em;
    font-weight: 700;
    color: {TEXT};
    margin: 20px 0 12px 0;
    letter-spacing: -0.01em;
    display: flex;
    align-items: center;
    gap: 8px;
    padding-bottom: 8px;
    border-bottom: 2px solid {BORDER};
    position: relative;
}}
.sec::after {{
    content: '';
    position: absolute;
    bottom: -2px; left: 0;
    height: 2px; width: 48px;
    background: linear-gradient(90deg, #3b82f6, #38bdf8);
    border-radius: 2px;
}}

/* Alert row card */
.alert-row {{
    background: {CARD_BG};
    border: 1px solid {BORDER};
    border-left: 4px solid #3b82f6;
    border-radius: 12px;
    padding: 14px 18px;
    margin: 8px 0;
    box-shadow: 0 1px 6px {SHADOW};
    animation: slideInLeft 0.4s ease both;
    transition: transform 0.18s, box-shadow 0.2s;
}}
.alert-row:hover {{
    transform: translateX(3px);
    box-shadow: 0 4px 16px {SHADOW};
}}

/* Outbreak card */
.outbreak-card {{
    background: {CARD_BG};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 16px 18px;
    margin: 8px 0;
    box-shadow: 0 1px 6px {SHADOW};
    animation: fadeIn 0.5s ease both;
    transition: transform 0.18s, box-shadow 0.2s;
}}
.outbreak-card:hover {{
    transform: translateY(-2px);
    box-shadow: 0 6px 20px {SHADOW};
}}

/* Chip buttons */
.stButton > button[data-chip] {{
    background: {BADGE_BG} !important;
    color: #2563eb !important;
    border: 1px solid #bfdbfe !important;
    border-radius: 20px !important;
    padding: 0.25em 1em !important;
    font-size: 0.82em !important;
    font-weight: 500 !important;
}}

/* Empty state */
.empty-state {{
    text-align: center;
    padding: 60px 20px;
    color: {TEXT_MUTED};
    animation: fadeIn 0.6s ease both;
}}
.empty-icon {{ font-size: 3.2em; margin-bottom: 14px; animation: scaleIn 0.7s ease both; }}
.empty-title {{ font-size: 1.05em; font-weight: 600; color: {TEXT}; margin-bottom: 6px; }}
.empty-desc  {{ font-size: 0.88em; }}

/* Divider */
hr {{ border-color: {DIVIDER} !important; }}

/* Scrollbar */
::-webkit-scrollbar {{ width: 5px; height: 5px; }}
::-webkit-scrollbar-track {{ background: {PAGE_BG}; }}
::-webkit-scrollbar-thumb {{ background: {BORDER}; border-radius: 4px; transition: background 0.2s; }}
::-webkit-scrollbar-thumb:hover {{ background: #3b82f6; }}

/* Tabs enhanced */
.stTabs [data-baseweb="tab"] {{
    position: relative;
    overflow: hidden;
}}
.stTabs [data-baseweb="tab"]::after {{
    content: '';
    position: absolute;
    bottom: 0; left: 50%;
    width: 0; height: 2px;
    background: #3b82f6;
    transition: all 0.3s;
    transform: translateX(-50%);
}}
.stTabs [data-baseweb="tab"]:hover::after {{
    width: 60%;
}}
</style>
"""


st.markdown(css(st.session_state["dark_mode"]), unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def _post(endpoint: str, **kwargs):
    try:
        resp = requests.post(f"{BACKEND_URL}{endpoint}", timeout=90, **kwargs)
        resp.raise_for_status()
        return resp.json(), None
    except requests.exceptions.ConnectionError:
        return None, "Cannot reach the backend. Is it running on port 8000?"
    except requests.exceptions.HTTPError as exc:
        return None, f"Server error {exc.response.status_code}: {exc.response.text[:200]}"
    except Exception as exc:
        return None, str(exc)


def _get(endpoint: str, params: Optional[dict] = None):
    try:
        resp = requests.get(f"{BACKEND_URL}{endpoint}", params=params, timeout=30)
        resp.raise_for_status()
        return resp.json(), None
    except requests.exceptions.ConnectionError:
        return None, "Cannot reach the backend."
    except Exception as exc:
        return None, str(exc)


def get_supported_languages():
    data, err = _get("/languages")
    if err or not data:
        return [
            {"code": "en", "name": "English"},
            {"code": "hi", "name": "Hindi (हिन्दी)"},
            {"code": "kn", "name": "Kannada (ಕನ್ನಡ)"},
            {"code": "ta", "name": "Tamil (தமிழ்)"},
            {"code": "te", "name": "Telugu (తెలుగు)"},
            {"code": "mr", "name": "Marathi (मराठी)"},
            {"code": "bn", "name": "Bengali (বাংলা)"},
        ]
    return data.get("languages", [])


def check_backend() -> bool:
    try:
        return requests.get(f"{BACKEND_URL}/health", timeout=5).status_code == 200
    except Exception:
        return False


def step_bar(current: int):
    steps = [("1", "Upload"), ("2", "Review"), ("3", "Results")]
    html = '<div class="steps">'
    for i, (num, label) in enumerate(steps):
        s = i + 1
        if s < current:
            nc, lc, sym = "done", "done", "✓"
        elif s == current:
            nc, lc, sym = "active", "active", num
        else:
            nc, lc, sym = "pending", "", num

        if i > 0:
            line_c = "done" if s <= current else "pending"
            html += f'<div class="step-line {line_c}"></div>'

        html += f"""
        <div class="step">
          <div class="step-num {nc}">{sym}</div>
          <div class="step-lbl {lc}">{label}</div>
        </div>"""
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


# ── Init ──────────────────────────────────────────────────────────────────────
if "supported_languages" not in st.session_state:
    st.session_state["supported_languages"] = get_supported_languages()
if "backend_online" not in st.session_state:
    st.session_state["backend_online"] = check_backend()

supported_langs = st.session_state["supported_languages"]
lang_options = {l["code"]: l["name"] for l in supported_langs}


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div class="sidebar-brand">'
        '<div class="sidebar-brand-title">🏥 MedReport AI</div>'
        '<div class="sidebar-brand-sub">AI-powered Medical Interpreter</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    # Status + theme row
    c1, c2, c3 = st.columns([3, 1, 1])
    with c1:
        dot = "dot-online" if st.session_state["backend_online"] else "dot-offline"
        label = "Online" if st.session_state["backend_online"] else "Offline"
        st.markdown(f'<span class="{dot}"></span><span class="status-text">{label}</span>', unsafe_allow_html=True)
    with c2:
        if st.button("↺", help="Ping backend", key="health_btn"):
            st.session_state["backend_online"] = check_backend()
            st.rerun()
    with c3:
        icon = "🌙" if st.session_state["dark_mode"] else "☀️"
        if st.button(icon, key="theme_btn", help="Toggle theme"):
            st.session_state["dark_mode"] = not st.session_state["dark_mode"]
            st.rerun()

    st.divider()
    st.markdown("**Settings**")

    language = st.selectbox(
        "Language",
        options=list(lang_options.keys()),
        format_func=lambda c: lang_options.get(c, c),
    )
    location = st.text_input("City / PIN Code", placeholder="Mumbai, 400001")
    phone    = st.text_input("Phone (SMS/WhatsApp)", placeholder="+91XXXXXXXXXX")
    symptoms = st.text_input("Known Symptoms", placeholder="fever, cough…")

    st.divider()
    st.caption(f"API  `{BACKEND_URL}`")


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="hero">'
    '  <div class="hero-title">🏥 MedReport AI</div>'
    '  <div class="hero-sub">AI-powered Medical Report Interpreter &nbsp;·&nbsp; Symptom Analysis &nbsp;·&nbsp; Outbreak Monitoring &nbsp;·&nbsp; Multilingual Support</div>'
    '</div>',
    unsafe_allow_html=True,
)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_upload, tab_chat, tab_dash, tab_hist = st.tabs([
    "📄  Report Analysis",
    "💬  Health Assistant",
    "🩺  Clinical Dashboard",
    "📊  Health History",
])


# ═════════════════════════════════════════════════════════════════════════════
# TAB 1 — Report Upload
# ═════════════════════════════════════════════════════════════════════════════
with tab_upload:
    step = st.session_state.get("step", 1)
    step_bar(step)
    st.divider()

    # ─ Step 1 ─
    if step == 1:
        st.markdown('<div class="sec">📂 Upload your Medical Report</div>', unsafe_allow_html=True)
        st.caption("PDF · PNG · JPG · JPEG · TXT — drag & drop or click")

        f = st.file_uploader("Choose file", type=["pdf","png","jpg","jpeg","txt"], label_visibility="collapsed")

        if f:
            size_kb = len(f.getvalue()) / 1024
            if f.type and f.type.startswith("image/"):
                c_img, c_meta = st.columns([1, 2])
                with c_img:
                    st.image(f, caption="Preview", use_container_width=True)
                with c_meta:
                    st.markdown(
                        f'<div class="card">'
                        f'<div class="card-title">📎 {f.name}</div>'
                        f'<div class="card-sub">{f.type} &nbsp;·&nbsp; {size_kb:.1f} KB</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
            else:
                st.markdown(
                    f'<div class="card">'
                    f'<div class="card-title">📎 {f.name}</div>'
                    f'<div class="card-sub">{f.type} &nbsp;·&nbsp; {size_kb:.1f} KB</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

            st.markdown("")
            if st.button("🔍 Extract Text", type="primary", use_container_width=True):
                with st.spinner("Reading report and extracting text…"):
                    res, err = _post("/extract-text", files={"file": (f.name, f.getvalue(), f.type)})
                if err:
                    st.error(f"Extraction failed: {err}")
                else:
                    st.session_state.update({
                        "extracted_text": (res or {}).get("extracted_text", "").strip(),
                        "uploaded_file_name": f.name,
                        "uploaded_file_type": f.type,
                        "uploaded_file_bytes": f.getvalue(),
                        "step": 2,
                    })
                    st.rerun()
        else:
            st.markdown(
                '<div class="empty-state">'
                '<div class="empty-icon">📋</div>'
                '<div class="empty-title">No file selected</div>'
                '<div class="empty-desc">Upload a medical report above to begin</div>'
                '</div>',
                unsafe_allow_html=True,
            )

    # ─ Step 2 ─
    elif step == 2:
        fname = st.session_state.get("uploaded_file_name", "")
        ftype = st.session_state.get("uploaded_file_type", "")
        if fname:
            st.info(f"📎 **{fname}** &nbsp;·&nbsp; `{ftype}`")

        st.markdown('<div class="sec">✏️ Review Extracted Text</div>', unsafe_allow_html=True)
        st.caption("OCR may have minor errors — correct them before AI analysis.")

        edited = st.text_area(
            "Text",
            value=st.session_state.get("extracted_text", ""),
            height=300,
            placeholder="Extracted text appears here. You can also paste manually.",
            label_visibility="collapsed",
        )
        n = len(edited.strip())
        q_color = "#22c55e" if n > 80 else "#f59e0b"
        q_label = "Good quality ✔" if n > 80 else "Add more text ⚠"

        cq1, cq2 = st.columns([1, 2])
        with cq1:
            st.markdown(f'<span style="color:{q_color}; font-size:0.84em; font-weight:600;">✏ {n:,} chars — {q_label}</span>', unsafe_allow_html=True)
        with cq2:
            st.progress(min(n / 500, 1.0))

        st.markdown("")
        cb, cn = st.columns([1, 2])
        with cb:
            if st.button("← Back", use_container_width=True):
                st.session_state["step"] = 1
                st.rerun()
        with cn:
            if st.button("🤖 Analyze with AI →", type="primary", use_container_width=True, disabled=(n == 0)):
                with st.spinner("Running AI analysis — this may take a moment…"):
                    res, err = _post(
                        "/process-report",
                        files={"file": (st.session_state.get("uploaded_file_name","report.txt"), edited.encode(), "text/plain")},
                        data={"language": language, "phone": phone.strip(), "location": location.strip(), "symptoms": symptoms.strip()},
                    )
                if err:
                    st.error(f"Analysis failed: {err}")
                else:
                    st.session_state["analysis_result"] = res
                    st.session_state["step"] = 3
                    st.rerun()

    # ─ Step 3 ─
    elif step == 3:
        res         = st.session_state.get("analysis_result", {})
        risk        = res.get("risk", {})
        risk_level  = risk.get("risk_level", "Unknown")
        risk_score  = risk.get("risk_score", 0)
        summary     = res.get("summary", "No summary available.")
        rec         = risk.get("recommendation", "")
        alerts_list = risk.get("alerts", [])

        # Risk banner
        r_icon  = {"High":"🔴","Moderate":"🟠","Low":"🟢"}.get(risk_level,"⚪")
        r_cls   = {"High":"risk-high","Moderate":"risk-moderate","Low":"risk-low"}.get(risk_level,"risk-low")
        r_color = {"High":"#ef4444","Moderate":"#d97706","Low":"#16a34a"}.get(risk_level,"#6b7280")
        st.markdown(
            f'<div class="{r_cls}">'
            f'<div class="risk-icon">{r_icon}</div>'
            f'<div>'
            f'  <div class="risk-text-level" style="color:{r_color};">{risk_level} Risk</div>'
            f'  <div class="risk-text-score">Score: {risk_score} / 10</div>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # Metrics
        lang_name = lang_options.get(language, language)
        st.markdown(
            f'<div class="metric-grid">'
            f'  <div class="metric"><div class="metric-val" style="color:{r_color}">{risk_score}</div><div class="metric-lbl">Risk Score</div></div>'
            f'  <div class="metric"><div class="metric-val">{len(alerts_list)}</div><div class="metric-lbl">Alerts</div></div>'
            f'  <div class="metric"><div class="metric-val" style="font-size:1.5em;">🌐</div><div class="metric-lbl">{lang_name}</div></div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # Summary
        st.markdown('<div class="sec">📋 Simplified Explanation</div>', unsafe_allow_html=True)
        display_summary = st.session_state.get("translated_summary", summary)
        current_lang    = st.session_state.get("translation_language", language)
        st.markdown(f'<div class="card">{display_summary}</div>', unsafe_allow_html=True)

        with st.expander("🌐 Translate to another language"):
            tl1, tl2 = st.columns([2,1])
            with tl1:
                new_lang = st.selectbox("Language", list(lang_options.keys()),
                                        format_func=lambda c: lang_options.get(c,c),
                                        key="tl_sel", label_visibility="collapsed")
            with tl2:
                if st.button("Translate", key="tl_btn", use_container_width=True):
                    if new_lang != current_lang:
                        with st.spinner(f"Translating to {lang_options.get(new_lang)}…"):
                            td, te = _post("/translate", json={"text": summary, "target_language": new_lang})
                        if te:
                            st.error(te)
                        else:
                            st.session_state["translated_summary"]  = td.get("translated_text", summary)
                            st.session_state["translation_language"] = new_lang
                            st.success("Translated!")
                            st.rerun()
                    else:
                        st.info("Already in this language.")

        if rec:
            st.markdown('<div class="sec">💡 Recommendation</div>', unsafe_allow_html=True)
            st.info(rec)

        if alerts_list:
            st.markdown('<div class="sec">⚠️ Medical Alerts</div>', unsafe_allow_html=True)
            for a in alerts_list:
                st.warning(f"⚠️ {a}")

        # Voice
        st.markdown('<div class="sec">🔊 Voice Explanation</div>', unsafe_allow_html=True)
        va1, va2 = st.columns([2,1])
        with va1:
            audio_mode = st.radio("Mode", ["full","sentence"],
                                  format_func=lambda x: "Full summary" if x=="full" else "Sentence by sentence",
                                  horizontal=True, key="audio_mode")
        with va2:
            slow_mode = st.checkbox("🐢 Slow", key="slow_mode")

        audio_text = st.session_state.get("translated_summary", summary)
        audio_lang = st.session_state.get("translation_language", language)
        slow_p     = "true" if slow_mode else "false"

        if audio_mode == "full":
            audio_url = f"{BACKEND_URL}/audio/explanation?text={requests.utils.quote(audio_text)}&language={audio_lang}&slow={slow_p}"
            st.audio(audio_url, format="audio/mp3")
            if st.button("💾 Download Audio", key="dl_audio"):
                try:
                    r = requests.get(audio_url, timeout=60)
                    if r.status_code == 200:
                        st.download_button("⬇️ Download MP3", r.content,
                                           file_name=f"report_audio_{audio_lang}.mp3", mime="audio/mp3")
                    else:
                        st.error("Audio generation failed.")
                except Exception as e:
                    st.error(str(e))
        else:
            st.caption("Each sentence plays individually:")
            with st.spinner("Generating sentence audio…"):
                path = f"/audio/sentences?text={requests.utils.quote(audio_text)}&language={audio_lang}&slow={slow_p}"
                sd, se = _get(path)
            if se:
                st.error(se)
            elif sd:
                import base64
                for si in sd.get("sentences", []):
                    idx, text, b64 = si.get("index",0), si.get("text",""), si.get("audio_base64","")
                    with st.expander(f"Sentence {idx+1}", expanded=(idx==0)):
                        st.markdown(f"_{text}_")
                        if b64:
                            st.audio(base64.b64decode(b64), format="audio/mp3")
            else:
                st.warning("No sentences found.")

        if phone.strip():
            st.caption(f"📱 Results sent to **{phone}** via SMS/WhatsApp.")

        # PDF Export
        rid = res.get("report_id")
        if rid:
            st.caption(f"Report ID: `{rid}`")
            st.divider()
            st.markdown('<div class="sec">📥 Export Report</div>', unsafe_allow_html=True)
            ep1, ep2 = st.columns([1,2])
            with ep1:
                if st.button("📄 Download PDF", use_container_width=True, type="secondary"):
                    try:
                        pr = requests.get(f"{BACKEND_URL}/export/pdf/{rid}", timeout=60)
                        if pr.status_code == 200:
                            st.download_button("⬇️ Download PDF", pr.content,
                                               file_name=f"report_{rid}.pdf", mime="application/pdf",
                                               use_container_width=True)
                            st.success("PDF ready!")
                        else:
                            st.error(f"PDF failed ({pr.status_code})")
                    except Exception as e:
                        st.error(str(e))
            with ep2:
                st.info("Includes risk assessment, AI summary, original text, and recommendations.")

        st.divider()
        n1, n2 = st.columns(2)
        with n1:
            if st.button("📄 Upload Another Report", use_container_width=True, type="primary"):
                for k in ["step","extracted_text","uploaded_file_name","uploaded_file_type",
                          "uploaded_file_bytes","analysis_result","translated_summary","translation_language"]:
                    st.session_state.pop(k, None)
                st.rerun()
        with n2:
            if st.button("✏️ Edit Extracted Text", use_container_width=True):
                st.session_state["step"] = 2
                st.rerun()


# ═════════════════════════════════════════════════════════════════════════════
# TAB 2 — Symptom Chatbot
# ═════════════════════════════════════════════════════════════════════════════
with tab_chat:
    ch1, ch2 = st.columns([4,1])
    with ch1:
        pass
    with ch2:
        if st.button("🗑 Clear", key="clear_chat"):
            st.session_state["chat_history"] = []
            st.session_state["session_id"] = uuid.uuid4().hex
            st.rerun()

    # Formal chat header
    st.markdown(
        '<div class="chat-header">'
        '  <div class="chat-header-avatar">👨‍⚕️</div>'
        '  <div>'
        '    <div class="chat-header-title">AI Health Assistant</div>'
        '    <div class="chat-header-sub">Describe your symptoms for evidence-based health guidance</div>'
        '  </div>'
        '  <div class="chat-header-badge">🟢 Active</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="chat-disclaimer">'
        '⚠️ <strong>Medical Disclaimer:</strong> This AI assistant provides general health information only. '
        'Always consult a qualified medical professional for diagnosis and treatment decisions.'
        '</div>',
        unsafe_allow_html=True,
    )

    if "session_id" not in st.session_state:
        st.session_state["session_id"] = uuid.uuid4().hex
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    if not st.session_state["chat_history"]:
        st.markdown(
            '<div class="empty-state" style="padding:40px 20px;">'
            '  <div class="empty-icon">💬</div>'
            '  <div class="empty-title">No conversation yet</div>'
            '  <div class="empty-desc">Use the quick symptom buttons below or type your question to begin.</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    # Quick chips
    st.markdown('<div style="font-size:0.85em; font-weight:600; color:inherit; margin:14px 0 6px 0; opacity:0.75; text-transform:uppercase; letter-spacing:0.05em;">Common Symptoms</div>', unsafe_allow_html=True)
    CHIPS = ["Fever", "Cough", "Headache", "Fatigue", "Chest pain", "Nausea", "Body ache", "Shortness of breath"]
    chip_cols = st.columns(len(CHIPS))
    for i, sym in enumerate(CHIPS):
        with chip_cols[i]:
            if st.button(sym, key=f"chip_{sym}", use_container_width=True):
                cur = st.session_state.get("chip_val", "")
                st.session_state["chip_val"] = f"{cur}, {sym}".strip(", ") if sym not in cur else cur
                st.rerun()

    sym_input = st.text_input(
        "Symptoms",
        value=st.session_state.get("chip_val", ""),
        placeholder="fever, cough, headache…",
        key="chat_sym",
        label_visibility="collapsed",
    )
    st.session_state["chip_val"] = sym_input
    chat_syms = [s.strip() for s in sym_input.split(",") if s.strip()]

    for entry in st.session_state["chat_history"]:
        with st.chat_message(entry["role"]):
            st.markdown(entry["text"])

    user_msg = st.chat_input("Describe your symptoms or ask a health question…")
    if user_msg:
        with st.chat_message("user"):
            st.markdown(user_msg)
        st.session_state["chat_history"].append({"role":"user","text":user_msg})

        typing_placeholder = st.empty()
        typing_placeholder.markdown(
            '<div class="typing-indicator">'
            '<span class="tdot"></span>'
            '<span class="tdot"></span>'
            '<span class="tdot"></span>'
            '<span style="font-size:0.8em; color:inherit; opacity:0.6; margin-left:6px;">Analyzing…</span>'
            '</div>',
            unsafe_allow_html=True,
        )
        data, err = _post("/chatbot", json={
            "session_id": st.session_state["session_id"],
            "message": user_msg,
            "symptoms": chat_syms,
        })
        typing_placeholder.empty()

        if err:
            with st.chat_message("assistant"):
                st.error(f"Chatbot unavailable: {err}")
        else:
            reply = data.get("response","")
            fups  = data.get("prompts",[])
            if fups:
                reply += "\n\n**Follow-up questions:**\n" + "\n".join(f"- {q}" for q in fups)
            with st.chat_message("assistant"):
                st.markdown(reply)
            st.session_state["chat_history"].append({"role":"assistant","text":reply})


# ═════════════════════════════════════════════════════════════════════════════
# TAB 3 — Doctor Dashboard
# ═════════════════════════════════════════════════════════════════════════════
with tab_dash:
    st.markdown('<div class="sec">🩺 Doctor Dashboard</div>', unsafe_allow_html=True)
    da1, da2 = st.columns(2)

    # ── Alerts ──
    with da1:
        st.markdown("**📋 Doctor Alerts**")

        with st.expander("➕ Post New Alert"):
            with st.form("alert_form", clear_on_submit=True):
                doc_name    = st.text_input("Doctor Name", placeholder="Dr. Sharma")
                a_region    = st.text_input("Region", placeholder="Mumbai")
                a_title     = st.text_input("Alert Title", placeholder="Dengue warning")
                a_message   = st.text_area("Message", height=90, placeholder="Describe the alert…")
                submitted   = st.form_submit_button("📢 Post Alert", use_container_width=True)
            if submitted:
                if all([doc_name, a_region, a_title, a_message]):
                    d, e = _post("/doctor/alerts", json={
                        "doctor_name": doc_name,"region": a_region,
                        "title": a_title,"message": a_message,
                    })
                    if e:
                        st.error(e)
                    else:
                        st.success(f"Posted (ID: {d.get('id')})")
                        fresh, _ = _get("/doctor/alerts", params={"region":""})
                        if fresh:
                            st.session_state["doctor_alerts"] = fresh.get("alerts",[])
                else:
                    st.warning("Fill in all fields.")

        fc1, fc2 = st.columns([3,1])
        with fc1:
            rf = st.text_input("Filter region", key="af", placeholder="All")
        with fc2:
            st.markdown("")
            if st.button("↺ Refresh", key="raf", use_container_width=True):
                d, e = _get("/doctor/alerts", params={"region": rf})
                st.session_state["doctor_alerts"] = d.get("alerts",[]) if not e else []

        if "doctor_alerts" not in st.session_state:
            d, e = _get("/doctor/alerts", params={"region":""})
            st.session_state["doctor_alerts"] = d.get("alerts",[]) if not e else []

        alerts = st.session_state.get("doctor_alerts",[])
        if alerts:
            st.caption(f"{len(alerts)} alert(s)")
            for a in alerts:
                dt = (a.get("created_at","") or "")[:10]
                st.markdown(
                    f'<div class="alert-row">'
                    f'<div style="display:flex; justify-content:space-between; align-items:flex-start;">'
                    f'  <span style="font-weight:700; font-size:0.95em;">{a.get("title","")}</span>'
                    f'  <span style="font-size:0.78em; opacity:0.6;">{dt}</span>'
                    f'</div>'
                    f'<div style="font-size:0.82em; opacity:0.7; margin:3px 0;">📍 {a.get("region","")} · 👨‍⚕️ {a.get("doctor","")}</div>'
                    f'<div style="font-size:0.88em; margin-top:6px;">{a.get("message","")}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown('<div class="empty-state"><div class="empty-icon">📭</div><div class="empty-desc">No alerts found.</div></div>', unsafe_allow_html=True)

    # ── Outbreaks ──
    with da2:
        st.markdown("**🦠 Outbreak Monitor**")

        oc1, oc2 = st.columns([2,1])
        with oc1:
            ob_region = st.text_input("Filter region", key="obf", placeholder="All")
        with oc2:
            st.markdown("")
            scan_clicked = st.button("🔍 Scan", key="scan_ob", use_container_width=True)

        if scan_clicked:
            with st.spinner("Scanning for outbreak clusters…"):
                d, e = _get("/outbreaks", params={"region": ob_region})
            if e:
                st.error(e)
            else:
                st.session_state["outbreak_clusters"] = d.get("clusters",[])

        clusters = st.session_state.get("outbreak_clusters")
        if clusters is None:
            st.markdown('<div class="empty-state"><div class="empty-icon">🔍</div><div class="empty-desc">Press Scan to detect clusters.</div></div>', unsafe_allow_html=True)
        elif not clusters:
            st.success("✅ No active outbreak clusters detected.")
        else:
            st.caption(f"{len(clusters)} cluster(s) found")
            for c in clusters:
                pct = int(c.get("risk_score",0) * 100)
                bar_color = "#ef4444" if pct >= 70 else ("#f59e0b" if pct >= 40 else "#22c55e")
                st.markdown(
                    f'<div class="outbreak-card">'
                    f'<div style="font-weight:700;">📍 {c.get("location","Unknown")}</div>'
                    f'<div style="font-size:0.84em; opacity:0.7; margin:3px 0;">Cause: {c.get("suspected_cause","N/A")} · Cases: {c.get("cases",0)}</div>'
                    f'<div style="display:flex; align-items:center; gap:10px; margin-top:8px;">'
                    f'  <div style="flex:1; height:6px; background:#e2e8f0; border-radius:3px;">'
                    f'    <div style="width:{pct}%; height:100%; background:{bar_color}; border-radius:3px; transition:width 0.5s;"></div>'
                    f'  </div>'
                    f'  <span style="font-size:0.82em; font-weight:700; color:{bar_color}; min-width:36px;">{pct}%</span>'
                    f'</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )


# ═════════════════════════════════════════════════════════════════════════════
# TAB 4 — Report History
# ═════════════════════════════════════════════════════════════════════════════
with tab_hist:
    hh1, hh2 = st.columns([4,1])
    with hh1:
        st.markdown('<div class="sec">📊 Report History & Comparison</div>', unsafe_allow_html=True)
        st.caption("Track health progress over time.")
    with hh2:
        if st.button("🗑 Clear All", key="cl_hist"):
            st.session_state["report_history"] = []
            st.rerun()

    if "report_history" not in st.session_state:
        st.session_state["report_history"] = []

    st.markdown("**📥 Upload Reports for Comparison**")
    multi_files = st.file_uploader("Upload reports", type=["pdf","png","jpg","jpeg","txt"],
                                   accept_multiple_files=True, key="multi_up")

    if multi_files and st.button("⚡ Process All", type="primary", use_container_width=True):
        prog = st.progress(0)
        status = st.empty()
        for i, mf in enumerate(multi_files):
            status.markdown(f"⏳ Processing **{mf.name}** ({i+1}/{len(multi_files)})…")
            r, e = _post("/process-report",
                         files={"file": (mf.name, mf.getvalue(), mf.type)},
                         data={"language": language, "phone":"", "location": location.strip(), "symptoms": symptoms.strip()})
            if not e and r:
                st.session_state["report_history"].append({
                    "filename":    mf.name,
                    "upload_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "report_id":   r.get("report_id"),
                    "risk_level":  r.get("risk",{}).get("risk_level","Unknown"),
                    "risk_score":  r.get("risk",{}).get("risk_score",0),
                    "summary":     r.get("summary",""),
                    "recommendation": r.get("risk",{}).get("recommendation",""),
                })
            else:
                st.error(f"Failed: {mf.name} — {e}")
            prog.progress((i+1)/len(multi_files))
        status.empty()
        st.success(f"✅ Processed {len(multi_files)} report(s).")
        st.rerun()

    history = st.session_state["report_history"]

    if history:
        st.divider()
        total     = len(history)
        hi, mo, lo = (sum(1 for r in history if r["risk_level"]==x) for x in ["High","Moderate","Low"])
        avg       = sum(r["risk_score"] for r in history) / total

        st.markdown(
            f'<div class="metric-grid">'
            f'<div class="metric"><div class="metric-val">{total}</div><div class="metric-lbl">Reports</div></div>'
            f'<div class="metric"><div class="metric-val" style="color:#ef4444">{hi}</div><div class="metric-lbl">High Risk</div></div>'
            f'<div class="metric"><div class="metric-val" style="color:#d97706">{mo}</div><div class="metric-lbl">Moderate</div></div>'
            f'<div class="metric"><div class="metric-val" style="color:#16a34a">{avg:.1f}</div><div class="metric-lbl">Avg Score</div></div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        if total >= 2:
            import plotly.graph_objects as go

            gc1, gc2 = st.columns([3,1])
            with gc1:
                st.markdown("**📈 Risk Score Trend**")
                scores = [r["risk_score"] for r in history]
                names  = [r["filename"][:18] for r in history]
                colors = ["#ef4444" if s>=6 else ("#f59e0b" if s>=3 else "#22c55e") for s in scores]
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=list(range(1, len(scores)+1)), y=scores,
                    mode="lines+markers",
                    line=dict(color="#3b82f6", width=2.5),
                    marker=dict(size=11, color=colors, line=dict(color="#fff",width=2)),
                    text=names, hovertemplate="<b>%{text}</b><br>Score: %{y}<extra></extra>",
                ))
                fig.add_hrect(y0=6, y1=10, fillcolor="#ef4444", opacity=0.06, line_width=0)
                fig.add_hrect(y0=3, y1=6,  fillcolor="#f59e0b", opacity=0.06, line_width=0)
                fig.add_hrect(y0=0, y1=3,  fillcolor="#22c55e", opacity=0.06, line_width=0)
                fig.update_layout(
                    xaxis_title="Report #", yaxis_title="Risk Score", yaxis=dict(range=[0,10]),
                    height=280, margin=dict(l=10,r=10,t=10,b=30),
                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                    hovermode="closest", showlegend=False,
                    xaxis=dict(tickmode="linear", dtick=1),
                )
                st.plotly_chart(fig, use_container_width=True)

            with gc2:
                st.markdown("**🥧 Distribution**")
                nz = [(l,v) for l,v in [("High",hi),("Moderate",mo),("Low",lo)] if v>0]
                if nz:
                    fig2 = go.Figure(go.Pie(
                        labels=[x[0] for x in nz], values=[x[1] for x in nz],
                        marker_colors=["#ef4444","#f59e0b","#22c55e"][:len(nz)],
                        hole=0.55, hovertemplate="%{label}: %{value}<extra></extra>",
                    ))
                    fig2.update_layout(
                        height=280, margin=dict(l=0,r=0,t=0,b=0),
                        showlegend=True, legend=dict(orientation="h", y=-0.15),
                        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                    )
                    st.plotly_chart(fig2, use_container_width=True)

        # Table
        st.markdown("**📋 Comparison Table**")
        import pandas as pd
        rows = []
        for i, r in enumerate(history, 1):
            icon = {"High":"🔴","Moderate":"🟠","Low":"🟢"}.get(r["risk_level"],"⚪")
            rows.append({"#":i,"File":r["filename"][:28],"Uploaded":r["upload_time"],
                         "Risk":f"{icon} {r['risk_level']}","Score":r["risk_score"],"ID":r["report_id"]})
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        # Detail cards
        st.divider()
        st.markdown("**📄 Detailed Reports**")
        for i, r in enumerate(history, 1):
            icon  = {"High":"🔴","Moderate":"🟠","Low":"🟢"}.get(r["risk_level"],"⚪")
            color = {"High":"#ef4444","Moderate":"#d97706","Low":"#16a34a"}.get(r["risk_level"],"#6b7280")
            with st.expander(f"{icon} Report {i}: {r['filename']} — {r['risk_level']}", expanded=(i==len(history))):
                di1, di2 = st.columns([3,1])
                with di1:
                    st.markdown(f'<span style="color:{color}; font-weight:800; font-size:1.1em;">{icon} {r["risk_level"]} Risk (Score: {r["risk_score"]})</span>', unsafe_allow_html=True)
                    st.caption(f"Uploaded: {r['upload_time']}  ·  ID: `{r['report_id']}`")
                    st.markdown(f'<div class="card">{r["summary"]}</div>', unsafe_allow_html=True)
                    if r["recommendation"]:
                        st.info(f"💡 {r['recommendation']}")
                with di2:
                    if st.button("📄 PDF", key=f"pdf_{i}", use_container_width=True):
                        try:
                            pr = requests.get(f"{BACKEND_URL}/export/pdf/{r['report_id']}", timeout=60)
                            if pr.status_code == 200:
                                st.download_button("⬇️ Download", pr.content,
                                                   file_name=f"report_{r['report_id']}.pdf",
                                                   mime="application/pdf",
                                                   key=f"dl_pdf_{i}", use_container_width=True)
                            else:
                                st.error("PDF failed")
                        except Exception as ex:
                            st.error(str(ex))
    else:
        st.markdown(
            '<div class="empty-state">'
            '<div class="empty-icon">📊</div>'
            '<div class="empty-title">No reports yet</div>'
            '<div class="empty-desc">Upload reports above to start tracking your health history.</div>'
            '</div>',
            unsafe_allow_html=True,
        )
