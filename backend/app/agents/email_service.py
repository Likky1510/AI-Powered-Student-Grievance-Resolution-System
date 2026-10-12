"""
Email notifications via SendGrid. In mock mode, just logs to console
instead of calling the real API -- lets you build/test the full
notification flow before signing up for SendGrid.
"""
import logging
from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger("notifications.email")
logging.basicConfig(level=logging.INFO)


def send_email(to_email: str, subject: str, body: str) -> bool:
    if settings.sendgrid_is_mocked:
        logger.info(f"[MOCK EMAIL] To: {to_email} | Subject: {subject}\n{body}")
        return True

    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail

    message = Mail(
        from_email=settings.sendgrid_from_email,
        to_emails=to_email,
        subject=subject,
        plain_text_content=body,
    )
    try:
        sg = SendGridAPIClient(settings.sendgrid_api_key)
        sg.send(message)
        return True
    except Exception as e:
        logger.error(f"SendGrid error: {e}")
        return False


def notify_grievance_submitted(to_email: str, grievance_id: str, category: str):
    send_email(
        to_email,
        subject="Your grievance has been received",
        body=(
            f"Your complaint (ID: {grievance_id}) has been received and "
            f"classified under '{category}'. You'll be notified as it progresses."
        ),
    )


def notify_staff_new_grievance(to_emails, grievance_id: str, category: str, student_email: str, department_name: str):
    if not to_emails:
        return
    if isinstance(to_emails, str):
        to_emails = [to_emails]

    subject = f"New grievance filed in {department_name}"
    body = (
        f"A new grievance has been filed by {student_email}.\n"
        f"Grievance ID: {grievance_id}\n"
        f"Category: {category}\n"
        f"Please review and update the status once it has been addressed."
    )

    for to_email in to_emails:
        send_email(to_email, subject=subject, body=body)


def notify_status_change(to_email: str, grievance_id: str, new_status: str):
    status_text = new_status.replace('_', ' ').title()
    if new_status == 'resolved':
        body = (
            f"Your complaint (ID: {grievance_id}) has been resolved. "
            "If you are satisfied with the outcome, no further action is required."
        )
    elif new_status == 'closed':
        body = (
            f"Your complaint (ID: {grievance_id}) has been closed. "
            "Thank you for using the grievance system."
        )
    else:
        body = f"Your complaint (ID: {grievance_id}) status changed to: {status_text}."

    send_email(
        to_email,
        subject=f"Grievance update: {status_text}",
        body=body,
    )
