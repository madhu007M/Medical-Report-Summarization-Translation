"""Enhanced Messaging Service with Test Mode & Validation.

Features:
- Test mode for development without real credentials
- Phone number validation
- Message history tracking
- Support for SMS and WhatsApp
- Detailed status reporting
"""
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional

from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

from ..config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# In-memory message history for test mode
_test_message_history: List[Dict[str, str]] = []


def _validate_phone_number(phone: str) -> bool:
    """Validate phone number format.

    Accepts: +1234567890, +91-1234567890, +44 20 1234 5678
    """
    if not phone:
        return False
    # Remove spaces and dashes for validation
    cleaned = phone.replace(" ", "").replace("-", "")
    # Must start with + and have 10-15 digits
    pattern = r'^\+\d{10,15}$'
    return bool(re.match(pattern, cleaned))


def _get_client() -> Optional[Client]:
    """Get Twilio client if credentials are configured."""
    if not settings.twilio_sid or not settings.twilio_token:
        return None
    # Check if credentials are placeholders
    if "your_twilio" in settings.twilio_sid.lower() or "your_twilio" in settings.twilio_token.lower():
        return None
    return Client(settings.twilio_sid, settings.twilio_token)


def is_twilio_configured() -> bool:
    """Check if Twilio is properly configured."""
    return _get_client() is not None


def send_message(destination: str, body: str, test_mode: bool = False) -> Dict[str, object]:
    """Send SMS or WhatsApp message with enhanced status tracking.

    Args:
        destination: Phone number (e.g., +91234567890 for SMS, whatsapp:+91234567890 for WhatsApp)
        body: Message content
        test_mode: If True, simulate sending without real API call

    Returns:
        {
            "success": bool,
            "status": "sent" | "failed" | "simulated" | "invalid_phone",
            "message": str,
            "timestamp": str,
            "destination": str
        }
    """
    timestamp = datetime.utcnow().isoformat()

    # Validate phone number
    phone = destination.replace("whatsapp:", "")
    if not _validate_phone_number(phone):
        logger.warning("Invalid phone number format: %s", destination)
        return {
            "success": False,
            "status": "invalid_phone",
            "message": "Invalid phone number format. Use international format: +1234567890",
            "timestamp": timestamp,
            "destination": destination,
        }

    # Test mode - simulate sending
    if test_mode or not is_twilio_configured():
        logger.info("TEST MODE: Simulated message to %s: %s", destination[:4] + "****", body[:50])
        _test_message_history.append({
            "destination": destination,
            "body": body,
            "timestamp": timestamp,
            "status": "simulated",
        })
        return {
            "success": True,
            "status": "simulated",
            "message": f"Test mode: Message simulated to {destination}",
            "timestamp": timestamp,
            "destination": destination,
        }

    # Real mode - send via Twilio
    client = _get_client()
    if not client:
        logger.warning("Twilio credentials missing or invalid; skipping SMS/WhatsApp send")
        return {
            "success": False,
            "status": "failed",
            "message": "Twilio credentials not configured. Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_FROM_NUMBER in .env",
            "timestamp": timestamp,
            "destination": destination,
        }

    try:
        message = client.messages.create(
            body=body,
            from_=settings.twilio_from,
            to=destination
        )
        logger.info("Message sent successfully to %s (SID: %s)", destination, message.sid)
        return {
            "success": True,
            "status": "sent",
            "message": f"Message sent successfully (SID: {message.sid})",
            "timestamp": timestamp,
            "destination": destination,
            "message_sid": message.sid,
        }
    except TwilioRestException as exc:
        logger.exception("Twilio send failed: %s", exc)
        return {
            "success": False,
            "status": "failed",
            "message": f"Twilio API error: {str(exc)}",
            "timestamp": timestamp,
            "destination": destination,
            "error_code": exc.code if hasattr(exc, 'code') else None,
        }


def get_test_message_history() -> List[Dict[str, str]]:
    """Get message history from test mode (for debugging/testing)."""
    return _test_message_history.copy()


def clear_test_message_history() -> None:
    """Clear test mode message history."""
    global _test_message_history
    _test_message_history = []
