"""
WhatsApp alerts via Twilio, used by the Escalation Agent for urgent/
overdue grievances. Mock mode logs instead of sending.
"""
import logging
from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger("notifications.whatsapp")


def send_whatsapp(to_number: str, body: str) -> bool:
    if settings.twilio_is_mocked:
        logger.info(f"[MOCK WHATSAPP] To: {to_number}\n{body}")
        return True

    from twilio.rest import Client

    try:
        client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
        client.messages.create(
            from_=settings.twilio_whatsapp_from,
            to=to_number,
            body=body,
        )
        return True
    except Exception as e:
        logger.error(f"Twilio error: {e}")
        return False


def notify_escalation(grievance_id: str, department_name: str, reason: str):
    send_whatsapp(
        settings.admin_whatsapp_to,
        body=(
            f"ESCALATION ALERT\nGrievance: {grievance_id}\n"
            f"Department: {department_name}\nReason: {reason}"
        ),
    )
