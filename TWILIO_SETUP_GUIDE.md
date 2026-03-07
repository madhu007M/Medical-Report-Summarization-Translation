# Twilio SMS/WhatsApp Setup Guide

Complete guide to setting up Twilio messaging for the AI Medical Report Interpreter platform.

## Overview

Twilio enables the platform to send:
- **SMS messages** - Medical report summaries and alerts
- **WhatsApp messages** - Same content via WhatsApp Business

**Optional Feature:** The platform works perfectly without Twilio. Messages will be simulated in test mode.

---

## Quick Start (Test Mode)

The platform includes a **test mode** that simulates messaging without real credentials:

```bash
# No setup needed - just run the platform
uvicorn backend.app.main:app --reload --port 8000
streamlit run frontend/streamlit_app.py
```

Test mode automatically activates when Twilio credentials are not configured. Messages are logged but not sent.

---

## Setting Up Real Twilio Integration

### Step 1: Create a Twilio Account

1. Go to [twilio.com/try-twilio](https://www.twilio.com/try-twilio)
2. Sign up for a free trial account
3. Verify your email and phone number

**Trial Account Limits:**
- $15.50 free credit
- Can send to verified phone numbers only
- Messages include "Sent from your Twilio trial account" prefix

### Step 2: Get Your Credentials

1. Log in to [Twilio Console](https://console.twilio.com/)
2. On the dashboard, find:
   - **Account SID** (starts with `AC...`)
   - **Auth Token** (click "Show" to reveal)
3. Copy both values

### Step 3: Get a Phone Number

#### For SMS:
1. In Twilio Console, go to **Phone Numbers** → **Manage** → **Buy a number**
2. Select your country
3. Check "SMS" capability
4. Purchase the number (free on trial)
5. Copy the phone number (format: `+1234567890`)

#### For WhatsApp:
1. Go to **Messaging** → **Try it out** → **Try WhatsApp**
2. Follow the sandbox setup instructions
3. Send the code from your WhatsApp to the Twilio number
4. Use the sandbox number: `whatsapp:+14155238886` (US) or your region's number

### Step 4: Configure Environment Variables

Edit your `.env` file:

```env
# Twilio Credentials
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_FROM_NUMBER=+12345678901
```

**Replace:**
- `AC1234...` with your actual Account SID
- `your_auth_token_here` with your actual Auth Token
- `+12345678901` with your Twilio phone number

### Step 5: Test the Integration

```bash
# Start the backend
uvicorn backend.app.main:app --reload --port 8000
```

Visit the API docs at `http://localhost:8000/docs` and test:

#### Check Configuration Status:
```
GET /messaging/status
```

#### Send a Test Message:
```
POST /messaging/send
{
  "phone": "+1234567890",
  "message": "Test message from Medical Report Platform",
  "test_mode": false
}
```

---

## Using WhatsApp Instead of SMS

### Format for WhatsApp Numbers:

Add `whatsapp:` prefix to the phone number:

```python
# SMS
phone = "+1234567890"

# WhatsApp
phone = "whatsapp:+1234567890"
```

### In the Frontend:

When entering phone numbers, users can specify:
- SMS: `+91234567890`
- WhatsApp: `whatsapp:+91234567890`

---

## Phone Number Validation

The platform validates phone numbers automatically:

**Valid Formats:**
- `+1234567890` (basic international format)
- `+91-1234567890` (with dashes)
- `+44 20 1234 5678` (with spaces)
- `whatsapp:+1234567890` (WhatsApp format)

**Invalid Formats:**
- `1234567890` (missing `+` prefix)
- `+12` (too short)
- `+123456789012345678` (too long)

---

## Message Templates

The platform sends structured messages:

### Report Summary Message (SMS/WhatsApp):
```
🏥 Medical Report Summary

Risk Level: [Low/Moderate/High]

[Simplified summary in patient's language]

Recommendation: [Actionable advice]
```

### Example:
```
🏥 Medical Report Summary

Risk Level: Moderate

आपके रक्तचाप में बढ़ोतरी दिखाई दे रही है।
कृपया नियमित रूप से इसकी जांच करें।

Recommendation: Schedule an urgent visit with a
doctor and monitor symptoms closely.
```

---

## Test Mode vs Production Mode

| Feature | Test Mode | Production Mode |
|---------|-----------|-----------------|
| **Activation** | Automatic (no credentials) | Manual (add credentials to .env) |
| **Messages Sent** | No (simulated) | Yes (real SMS/WhatsApp) |
| **Costs** | $0 | Twilio pricing |
| **Validation** | Yes | Yes |
| **Logging** | Yes (in-memory history) | Yes (Twilio console) |
| **Use Case** | Development, demos | Production, real users |

---

## Pricing (As of 2024)

### Twilio Costs:

**SMS:**
- USA: $0.0079 per message
- India: $0.0055 per message
- UK: $0.0400 per message

**WhatsApp:**
- User-initiated: $0.005 per message
- Business-initiated: $0.0042-0.0143 (varies by country)

**Phone Number Rental:**
- Local number: $1-$2/month
- Toll-free: $2-$5/month

**Trial Account:**
- $15.50 free credit
- ~2000 SMS messages (India) or ~500 SMS (UK)

---

## Troubleshooting

### "Twilio credentials not configured" Error

**Cause:** Placeholder values in `.env`

**Fix:** Replace `your_twilio_...` with actual credentials from Twilio Console

### "Invalid phone number format" Error

**Cause:** Phone number missing `+` or incorrect format

**Fix:** Use international format: `+[country_code][number]`
- India: `+919876543210`
- USA: `+12345678901`

### "Unverified phone number" Error (Trial Account)

**Cause:** Twilio trial accounts can only send to verified numbers

**Fix:**
1. Go to Twilio Console → **Phone Numbers** → **Verified Caller IDs**
2. Click **Add a new Caller ID**
3. Enter the recipient's phone number
4. Complete verification

### Messages Not Received

**Checks:**
1. ✅ Verify credentials are correct in `.env`
2. ✅ Check phone number format (must include `+` and country code)
3. ✅ Verify recipient number (trial accounts)
4. ✅ Check Twilio account balance
5. ✅ Check logs: `GET /messaging/test-history`

### WhatsApp Sandbox Not Working

**Fix:**
1. Ensure you've joined the sandbox by sending the code to Twilio's WhatsApp number
2. Use the correct sandbox number (changes by region)
3. Check WhatsApp sandbox status in Twilio Console

---

## API Endpoints Reference

### 1. Check Messaging Status
```http
GET /messaging/status
```

**Response:**
```json
{
  "configured": true,
  "provider": "Twilio",
  "test_mode_available": true,
  "status": "ready",
  "message": "Twilio is configured and ready to send messages"
}
```

### 2. Send Test Message
```http
POST /messaging/send
Content-Type: application/json

{
  "phone": "+1234567890",
  "message": "Test message",
  "test_mode": false
}
```

**Response:**
```json
{
  "success": true,
  "status": "sent",
  "message": "Message sent successfully (SID: SM...)",
  "timestamp": "2024-03-06T10:30:00.000Z",
  "destination": "+1234567890",
  "message_sid": "SM1234567890abcdef"
}
```

### 3. Get Test Message History
```http
GET /messaging/test-history
```

**Response:**
```json
{
  "history": [
    {
      "destination": "+1234567890",
      "body": "Test message",
      "timestamp": "2024-03-06T10:30:00.000Z",
      "status": "simulated"
    }
  ],
  "count": 1
}
```

---

## Security Best Practices

### 1. Protect Your Credentials

**Never commit `.env` to git:**
```bash
# .gitignore should include:
.env
```

**Use environment variables in production:**
```bash
export TWILIO_ACCOUNT_SID="AC..."
export TWILIO_AUTH_TOKEN="..."
export TWILIO_FROM_NUMBER="+..."
```

### 2. Rate Limiting

Add rate limits to prevent abuse:
```python
# In production, limit messages per user per day
MAX_MESSAGES_PER_DAY = 10
```

### 3. Phone Number Validation

The platform validates all phone numbers before sending. Never disable this validation.

---

## Production Deployment Checklist

- [ ] Upgrade to paid Twilio account (remove trial limitations)
- [ ] Purchase dedicated phone number or WhatsApp Business number
- [ ] Set up rate limiting (messages per user/day)
- [ ] Configure monitoring and alerts for failed messages
- [ ] Set up message delivery tracking
- [ ] Implement opt-out mechanism (required by law in many regions)
- [ ] Add message templates for different risk levels
- [ ] Test with real phone numbers in target regions
- [ ] Monitor Twilio usage and costs
- [ ] Set up billing alerts in Twilio Console

---

## Alternative: SMS Gateway Integration

If Twilio is not suitable, the platform can be adapted for other SMS providers:

**Supported Alternatives:**
- **AWS SNS** (Simple Notification Service)
- **Nexmo/Vonage** (Similar to Twilio)
- **Plivo** (Lower cost alternative)
- **MessageBird** (European focus)

To integrate, modify `backend/app/modules/messaging_service.py` with the provider's SDK.

---

## FAQs

**Q: Do I need Twilio for the platform to work?**
A: No. The platform works perfectly in test mode without Twilio. Messaging is optional.

**Q: Can I use my own SMS gateway?**
A: Yes. Modify `messaging_service.py` to integrate your preferred provider.

**Q: How much will it cost to send 1000 messages?**
A: In India: ~$5.50 (SMS). WhatsApp is cheaper at ~$4.20.

**Q: Can I send messages in regional languages?**
A: Yes! The platform automatically translates summaries before sending.

**Q: Is there a message length limit?**
A: SMS: 160 characters (extended to 1600 with segmentation). WhatsApp: 4096 characters.

---

## Getting Help

**Twilio Support:**
- Documentation: [twilio.com/docs](https://www.twilio.com/docs)
- Console: [console.twilio.com](https://console.twilio.com/)
- Support: [support.twilio.com](https://support.twilio.com/)

**Platform Support:**
- Check logs: `uvicorn backend.app.main:app` output
- Test endpoint: `GET /messaging/status`
- Review message history: `GET /messaging/test-history`

---

## Summary

✅ **Test mode** works out-of-the-box (no setup needed)
✅ **Phone validation** prevents invalid numbers
✅ **Both SMS and WhatsApp** supported
✅ **Multilingual** messages automatically translated
✅ **Trial account** provides free testing
✅ **Production ready** with proper credentials

**Time to setup:** 10-15 minutes
**Cost:** $0 (trial) or ~$0.005-0.01 per message (production)
