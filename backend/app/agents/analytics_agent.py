"""
Analytics Agent.

The actual bottleneck detection is plain SQL aggregation -- averages,
counts, rates. Claude is used only at the very end, to turn the numbers
into a short plain-English summary for admins. This mirrors the
"process intelligence" features described in the project spec without
asking an LLM to do arithmetic it might get wrong.
"""
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.models import Grievance, Department, GrievanceStatus
from app.agents.claude_client import call_claude_text


def get_department_stats(db: Session) -> list[dict]:
    departments = db.query(Department).all()
    stats = []

    for dept in departments:
        grievances = db.query(Grievance).filter(Grievance.department_id == dept.id).all()
        total = len(grievances)
        resolved = [g for g in grievances if g.resolved_at is not None]
        escalated = [g for g in grievances if g.is_escalated]

        resolution_hours = [
            (g.resolved_at - g.created_at).total_seconds() / 3600 for g in resolved
        ]
        avg_resolution = sum(resolution_hours) / len(resolution_hours) if resolution_hours else None

        sla_breaches = [
            g for g in resolved
            if (g.resolved_at - g.created_at).total_seconds() / 3600 > dept.sla_hours
        ]

        stats.append({
            "department_name": dept.name,
            "total_grievances": total,
            "resolved_count": len(resolved),
            "avg_resolution_hours": round(avg_resolution, 1) if avg_resolution else None,
            "escalation_rate": round(len(escalated) / total, 2) if total else 0.0,
            "sla_breach_rate": round(len(sla_breaches) / len(resolved), 2) if resolved else 0.0,
        })

    return stats


def get_category_stats(db: Session) -> list[dict]:
    rows = (
        db.query(Grievance.category, func.count(Grievance.id))
        .group_by(Grievance.category)
        .all()
    )
    stats = []
    for category, count in rows:
        if category is None:
            continue
        grievances = db.query(Grievance).filter(Grievance.category == category).all()
        resolved = [g for g in grievances if g.resolved_at is not None]
        hours = [(g.resolved_at - g.created_at).total_seconds() / 3600 for g in resolved]
        avg = round(sum(hours) / len(hours), 1) if hours else None
        stats.append({"category": category.value, "total": count, "avg_resolution_hours": avg})
    return stats


def get_summary_counts(db: Session) -> dict:
    total = db.query(Grievance).count()
    resolved = db.query(Grievance).filter(Grievance.status == GrievanceStatus.resolved).count()
    escalated = db.query(Grievance).filter(Grievance.is_escalated == True).count()  # noqa: E712
    pending = total - resolved
    return {"total_grievances": total, "resolved": resolved, "pending": pending, "escalated": escalated}


def generate_ai_summary(dept_stats: list[dict], category_stats: list[dict], counts: dict) -> str:
    """Turns the computed numbers into a short, readable insight paragraph."""
    mock = (
        "[mock summary] Based on current data, review department stats for "
        "the highest escalation_rate and sla_breach_rate to identify bottlenecks."
    )
    if not dept_stats and not category_stats:
        return "Not enough data yet to generate insights."

    prompt = (
        f"Summary counts: {counts}\n"
        f"Per-department stats: {dept_stats}\n"
        f"Per-category stats: {category_stats}\n\n"
        "Write a 3-4 sentence plain-English summary for a college admin, "
        "highlighting which department or category is the biggest bottleneck "
        "and one concrete suggestion. Do not just restate the numbers."
    )
    return call_claude_text(
        system_prompt="You are a process-improvement analyst summarizing grievance system metrics for a college administrator.",
        user_prompt=prompt,
        mock_response=mock,
    )
