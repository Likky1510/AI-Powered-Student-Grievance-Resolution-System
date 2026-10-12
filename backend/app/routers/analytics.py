from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import require_role
from app.models.models import UserRole
from app.models.schemas import AnalyticsSummary
from app.agents.analytics_agent import (
    get_department_stats, get_category_stats, get_summary_counts, generate_ai_summary,
)
from app.agents.escalation_agent import check_and_escalate

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary", response_model=AnalyticsSummary)
def analytics_summary(
    db: Session = Depends(get_db),
    current_user=Depends(require_role(UserRole.admin)),
):
    """
    The 'Process Intelligence' endpoint: bottlenecks, rejection/escalation
    rates, and an AI-generated plain-English summary for admins.
    """
    counts = get_summary_counts(db)
    dept_stats = get_department_stats(db)
    category_stats = get_category_stats(db)
    ai_summary = generate_ai_summary(dept_stats, category_stats, counts)

    return AnalyticsSummary(
        total_grievances=counts["total_grievances"],
        resolved=counts["resolved"],
        pending=counts["pending"],
        escalated=counts["escalated"],
        by_department=dept_stats,
        by_category=category_stats,
        ai_summary=ai_summary,
    )


@router.post("/run-escalation-check")
def run_escalation_check(
    db: Session = Depends(get_db),
    current_user=Depends(require_role(UserRole.admin)),
):
    """
    Manually trigger the Escalation Agent (normally run on a schedule --
    see app/core/scheduler.py). Useful for demos/testing.
    """
    escalated_ids = check_and_escalate(db)
    return {"escalated_count": len(escalated_ids), "grievance_ids": escalated_ids}
