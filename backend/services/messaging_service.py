"""
Messaging Service — sends SMS and WhatsApp messages via Twilio.

Falls back gracefully when Twilio credentials are not configured.
"""

import logging
from typing import Optional

from backend.config import (
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_PHONE_NUMBER,
    TWILIO_WHATSAPP_NUMBER,
)

logger = logging.getLogger(__name__)


def _get_twilio_client():
    """Return an authenticated Twilio Client or None if credentials are missing."""
    if not (TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN):
        logger.warning("Twilio credentials not configured — messaging disabled.")
        return None
    try:
        from twilio.rest import Client
        return Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    except ImportError:
        logger.warning("twilio package not installed — messaging disabled.")
        return None
    except Exception as exc:
        logger.error("Failed to initialise Twilio client: %s", exc)
        return None


def send_sms(to_number: str, message: str) -> dict:
    """
    Send an SMS to *to_number*.

    Args:
        to_number: Recipient phone in E.164 format, e.g. '+919876543210'.
        message:   Text body (max ~1600 chars for multi-part SMS).

    Returns:
        {'success': bool, 'sid': str | None, 'error': str | None}
    """
    client = _get_twilio_client()
    if client is None:
        return {"success": False, "sid": None, "error": "Twilio not configured."}

    if not TWILIO_PHONE_NUMBER:
        return {"success": False, "sid": None, "error": "TWILIO_PHONE_NUMBER not set."}

    try:
        msg = client.messages.create(
            body=message[:1600],
            from_=TWILIO_PHONE_NUMBER,
            to=to_number,
        )
        logger.info("SMS sent to %s: SID=%s", to_number, msg.sid)
        return {"success": True, "sid": msg.sid, "error": None}
    except Exception as exc:
        logger.error("SMS send failed: %s", exc)
        return {"success": False, "sid": None, "error": str(exc)}


def send_whatsapp(to_number: str, message: str) -> dict:
    """
    Send a WhatsApp message.

    Args:
        to_number: Recipient number in E.164 format (prefix with 'whatsapp:' is added automatically).
        message:   Text body.

    Returns:
        {'success': bool, 'sid': str | None, 'error': str | None}
    """
    client = _get_twilio_client()
    if client is None:
        return {"success": False, "sid": None, "error": "Twilio not configured."}

    if not TWILIO_WHATSAPP_NUMBER:
        return {"success": False, "sid": None, "error": "TWILIO_WHATSAPP_NUMBER not set."}

    wa_to = f"whatsapp:{to_number}" if not to_number.startswith("whatsapp:") else to_number

    try:
        msg = client.messages.create(
            body=message[:1600],
            from_=TWILIO_WHATSAPP_NUMBER,
            to=wa_to,
        )
        logger.info("WhatsApp sent to %s: SID=%s", to_number, msg.sid)
        return {"success": True, "sid": msg.sid, "error": None}
    except Exception as exc:
        logger.error("WhatsApp send failed: %s", exc)
        return {"success": False, "sid": None, "error": str(exc)}


def send_report_summary(
    phone: str,
    summary: str,
    risk_level: str,
    via_whatsapp: bool = False,
) -> dict:
    """
    Convenience function — sends a formatted medical report summary.

    Args:
        phone:        Recipient phone number (E.164).
        summary:      Patient-friendly summary text.
        risk_level:   'Low', 'Moderate', or 'High'.
        via_whatsapp: If True, use WhatsApp; otherwise use SMS.
    """
    emoji = {"Low": "✅", "Moderate": "⚠️", "High": "🚨"}.get(risk_level, "ℹ️")
    body = (
        f"{emoji} Medical Report Summary\n"
        f"Risk Level: {risk_level}\n\n"
        f"{summary[:800]}\n\n"
        f"For the full report and voice explanation, visit the platform."
    )
    if via_whatsapp:
        return send_whatsapp(phone, body)
    return send_sms(phone, body)


def broadcast_alert(
    phone_numbers: list,
    title: str,
    message: str,
    via_whatsapp: bool = False,
) -> list:
    """
    Broadcast a health alert to a list of phone numbers.

    Returns a list of result dicts, one per number.
    """
    body = f"🏥 Health Alert: {title}\n\n{message[:1000]}"
    results = []
    for phone in phone_numbers:
        if via_whatsapp:
            results.append(send_whatsapp(phone, body))
        else:
            results.append(send_sms(phone, body))
    return results
