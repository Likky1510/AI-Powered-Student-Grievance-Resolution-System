"""
Classification Agent + Priority Detection Agent.

Combined into a single Claude call on purpose: both tasks read the same
input (the complaint text) and produce small structured fields. Splitting
them into two separate API calls would double latency and cost for no
real benefit. This is the kind of call you should make explicitly when
designing a "multi-agent" system -- not every named agent needs its own
LLM round-trip.
"""
from app.agents.claude_client import call_claude_json
from app.models.models import GrievanceCategory, GrievancePriority

VALID_CATEGORIES = [c.value for c in GrievanceCategory]
VALID_PRIORITIES = [p.value for p in GrievancePriority]

SYSTEM_PROMPT = f"""You are a grievance triage assistant for a college student complaint system.

Given a student's complaint text, do two things:
1. Classify it into EXACTLY one of these categories: {VALID_CATEGORIES}
2. Assign a priority level from: {VALID_PRIORITIES}
   - urgent: safety, harassment, health emergencies, same-day deadlines
   - high: financial deadlines, certificate deadlines blocking opportunities, repeated unresolved issues
   - medium: standard academic/hostel/attendance issues affecting one student
   - low: general questions, minor inconveniences, non-time-sensitive requests

Respond with ONLY a JSON object, no preamble, no markdown fences, no explanation outside the JSON:
{{
  "category": "<one of the categories above>",
  "category_reason": "<one short sentence explaining why>",
  "priority": "<one of the priorities above>",
  "priority_reason": "<one short sentence explaining why>"
}}
"""


def _keyword_mock(text: str) -> dict:
    """
    Rule-based stand-in used when ANTHROPIC_API_KEY=mock.
    Simple keyword matching -- good enough to exercise the rest of the
    pipeline (routing, DB writes, notifications) without a real API key.
    """
    lower = text.lower()

    category_keywords = {
        "fees": ["fee", "payment", "scholarship", "refund", "tuition due"],
        "hostel": ["hostel", "warden", "mess food", "roommate", "hostel room"],
        "attendance": ["attendance", "absent", "shortage", "condonation"],
        "certificates": ["certificate", "transcript", "bonafide", "marksheet"],
        "academic": ["exam", "grade", "marks", "professor", "lecture", "syllabus"],
        "infrastructure": ["wifi", "internet", "computer lab", "classroom", "lift", "washroom", "electricity"],
    }
    # Score every category by how many of its keywords appear, instead of
    # taking the first dict entry that matches even one keyword -- a
    # first-match approach picks the wrong category whenever a complaint
    # mentions an incidental word (e.g. "scholarship deadline" for a
    # certificate request) that happens to belong to an earlier category.
    scores = {cat: sum(1 for kw in kws if kw in lower) for cat, kws in category_keywords.items()}
    best_cat, best_score = max(scores.items(), key=lambda kv: kv[1])
    category = best_cat if best_score > 0 else "other"

    urgent_keywords = ["harass", "emergency", "medical", "today", "safety", "threat"]
    high_keywords = ["deadline", "urgent", "immediately", "blocked", "rejected again"]

    if any(kw in lower for kw in urgent_keywords):
        priority = "urgent"
    elif any(kw in lower for kw in high_keywords):
        priority = "high"
    elif category in ("fees", "certificates"):
        priority = "medium"
    else:
        priority = "low"

    return {
        "category": category,
        "category_reason": f"[mock] matched keyword rules for '{category}'",
        "priority": priority,
        "priority_reason": f"[mock] matched keyword rules for '{priority}' priority",
    }


def classify_and_prioritize(complaint_text: str) -> dict:
    """
    Returns: {category, category_reason, priority, priority_reason}
    Falls back to safe defaults if Claude's response is malformed.
    """
    mock = _keyword_mock(complaint_text)
    result = call_claude_json(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=f"Complaint:\n\"\"\"\n{complaint_text}\n\"\"\"",
        mock_response=mock,
    )

    # Defensive validation -- never trust LLM output blindly, even in production mode
    if result.get("category") not in VALID_CATEGORIES:
        result["category"] = "other"
        result["category_reason"] = "Could not confidently classify; defaulted to 'other'."
    if result.get("priority") not in VALID_PRIORITIES:
        result["priority"] = "medium"
        result["priority_reason"] = "Could not confidently assess priority; defaulted to 'medium'."

    return result
