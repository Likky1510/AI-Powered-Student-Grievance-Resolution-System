"""
Department Routing Agent.

Deliberately NOT an LLM call in the common case: category -> department
is a deterministic lookup once classification is done. We only spend an
extra Claude call when the complaint text suggests it might span two
departments (e.g. a hostel issue that's really about fees), which is rare.
This keeps routing fast, free, and 100% predictable for the 95% case.
"""
from sqlalchemy.orm import Session

from app.agents.claude_client import call_claude_json
from app.models.models import Department, GrievanceCategory

AMBIGUOUS_HINTS = ["also", "as well as", "and also", "both", "additionally"]


def _is_possibly_ambiguous(text: str) -> bool:
    lower = text.lower()
    return any(hint in lower for hint in AMBIGUOUS_HINTS)


def route_to_department(db: Session, category: str, complaint_text: str) -> Department:
    """
    Looks up the Department row matching `category`. If the complaint text
    hints at overlap between departments, asks Claude to pick the single
    best primary department instead of guessing silently.
    """
    department = db.query(Department).filter(Department.category == category).first()

    if department is None:
        # Fallback: route anything unmapped to the "other" / general department
        department = db.query(Department).filter(Department.category == GrievanceCategory.other).first()

    if _is_possibly_ambiguous(complaint_text) and department is not None:
        all_depts = db.query(Department).all()
        dept_names = [d.name for d in all_depts]

        mock_response = {"department": department.name, "reason": "[mock] kept primary category match"}
        result = call_claude_json(
            system_prompt=(
                "You route student complaints to ONE primary department. "
                f"Available departments: {dept_names}. "
                "Respond ONLY with JSON: {\"department\": \"<name>\", \"reason\": \"<short reason>\"}"
            ),
            user_prompt=f"Complaint:\n{complaint_text}\n\nSuggested category match: {department.name}",
            mock_response=mock_response,
        )
        chosen_name = result.get("department")
        match = next((d for d in all_depts if d.name == chosen_name), None)
        if match:
            department = match

    return department
