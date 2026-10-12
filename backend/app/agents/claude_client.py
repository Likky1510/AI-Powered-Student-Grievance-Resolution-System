"""
Thin wrapper around the Anthropic API used by all agents.

If ANTHROPIC_API_KEY is "mock" (see .env.example), `call_claude_json`
skips the real network call and returns a rule-based simulated response,
so the rest of the app (routing, DB writes, notifications, frontend)
can be built and tested with zero API cost / before you have a key.

Swap in a real key later and nothing else in the codebase needs to change.
"""
import json
import re
from typing import Optional

from app.core.config import get_settings

settings = get_settings()

_client = None


def _get_client():
    global _client
    if _client is None:
        import anthropic
        _client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    return _client


def _strip_json_fences(text: str) -> str:
    """Claude sometimes wraps JSON in ```json ... ``` even when told not to."""
    text = text.strip()
    text = re.sub(r"^```json\s*|^```\s*|```$", "", text, flags=re.MULTILINE).strip()
    return text


def call_claude_json(system_prompt: str, user_prompt: str, mock_response: dict) -> dict:
    """
    Calls Claude with a system+user prompt and expects a JSON object back.
    In mock mode, returns `mock_response` unchanged (callers pass in a
    keyword-rule-based guess so mock mode still behaves sensibly).
    """
    if settings.claude_is_mocked:
        return mock_response

    client = _get_client()
    response = client.messages.create(
        model=settings.claude_model,
        max_tokens=1000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    raw_text = "".join(
        block.text for block in response.content if block.type == "text"
    )
    cleaned = _strip_json_fences(raw_text)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Fall back gracefully rather than crashing the whole request
        return {"error": "Could not parse Claude response", "raw": raw_text}


def call_claude_text(system_prompt: str, user_prompt: str, mock_response: str) -> str:
    """Same as above but for free-text responses (e.g. the analytics summary)."""
    if settings.claude_is_mocked:
        return mock_response

    client = _get_client()
    response = client.messages.create(
        model=settings.claude_model,
        max_tokens=600,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return "".join(block.text for block in response.content if block.type == "text")
