"""
Runs the Escalation Agent automatically every N minutes using APScheduler,
so SLA breaches get caught without anyone needing to call the manual
/analytics/run-escalation-check endpoint.
"""
import logging
from apscheduler.schedulers.background import BackgroundScheduler

from app.db.session import SessionLocal
from app.agents.escalation_agent import check_and_escalate

logger = logging.getLogger("scheduler")
scheduler = BackgroundScheduler()


def _scheduled_escalation_check():
    db = SessionLocal()
    try:
        escalated = check_and_escalate(db)
        if escalated:
            logger.info(f"Scheduled check escalated {len(escalated)} grievance(s)")
    finally:
        db.close()


def start_scheduler():
    # Every 30 minutes is reasonable for a demo; tighten for production.
    scheduler.add_job(_scheduled_escalation_check, "interval", minutes=30, id="escalation_check")
    scheduler.start()
    logger.info("Background scheduler started (escalation check every 30 min)")


def stop_scheduler():
    scheduler.shutdown(wait=False)
