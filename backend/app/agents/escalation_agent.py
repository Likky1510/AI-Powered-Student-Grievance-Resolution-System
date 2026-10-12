"""
Escalation Agent.

This is intentionally rule-based, not an LLM call: "has this grievance
been unresolved longer than its department's SLA?" is a deterministic
time comparison. Running this through an LLM would add latency and cost
with zero benefit -- the rule IS the logic.

Called periodically by the scheduler (see app/core/scheduler.py).
"""
import logging
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.models import Grievance, GrievanceStatus, Department
from app.agents.whatsapp_service import notify_escalation
from app.agents.email_service import send_email

logger = logging.getLogger("agents.escalation")

OPEN_STATUSES = [
    GrievanceStatus.submitted,
    GrievanceStatus.categorized,
    GrievanceStatus.assigned,
    GrievanceStatus.in_progress,
]


def check_and_escalate(db: Session) -> list[str]:
    """
    Scans all open grievances; escalates any that have exceeded their
    department's SLA. Returns list of escalated grievance IDs.
    """
    from app.models.models import StatusHistory, Escalation

    escalated_ids = []
    open_grievances = (
        db.query(Grievance)
        .filter(Grievance.status.in_(OPEN_STATUSES))
        .all()
    )

    for g in open_grievances:
        if not g.department_id:
            continue
        department = db.query(Department).filter(Department.id == g.department_id).first()
        if not department:
            continue

        sla_deadline = g.created_at + timedelta(hours=department.sla_hours)
        if datetime.utcnow() > sla_deadline and not g.is_escalated:
            g.is_escalated = True
            g.escalation_count += 1
            g.status = GrievanceStatus.escalated

            reason = (
                f"SLA breached: created {g.created_at.isoformat()}, "
                f"target {department.sla_hours}h, still open."
            )
            db.add(Escalation(grievance_id=g.id, reason=reason, escalated_to="Department Head"))
            db.add(StatusHistory(grievance_id=g.id, status=GrievanceStatus.escalated, note=reason))

            notify_escalation(g.id, department.name, reason)
            if department.contact_email:
                send_email(
                    department.contact_email,
                    subject=f"[ESCALATED] Grievance {g.id} overdue",
                    body=reason,
                )

            escalated_ids.append(g.id)
            logger.info(f"Escalated grievance {g.id}: {reason}")

    db.commit()
    return escalated_ids
