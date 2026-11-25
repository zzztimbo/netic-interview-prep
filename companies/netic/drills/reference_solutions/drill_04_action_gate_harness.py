"""Reference solution for Drill 4: Single-LLM Action-Gating Execution Harness."""

from __future__ import annotations

import json
import re
from typing import Any, Awaitable, Callable


FALLBACK_REPLY = "I want to make sure I get this right — could you repeat what time works best for you?"
SLOT_CONFLICT_REPLY = "That time slot was just taken — let me check the next available time for you."

_FENCE_RE = re.compile(r"^\s*```(?:json)?\s*(.*?)\s*```\s*$", re.DOTALL | re.IGNORECASE)
_VALID_ACTIONS = {"BOOK", "ASK_CLARIFICATION", "NO_AVAILABILITY"}


def _parse_llm_json(raw: str) -> dict[str, Any] | None:
    if not isinstance(raw, str) or not raw.strip():
        return None
    cleaned = raw.strip()
    match = _FENCE_RE.match(cleaned)
    if match:
        cleaned = match.group(1).strip()
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


async def execute_agent_turn(
    raw_llm_output: str,
    customer_id: str,
    open_slots: list[str],
    book_slot_fn: Callable[[str, str], Awaitable[bool]],
) -> dict:
    decision = _parse_llm_json(raw_llm_output)
    if decision is None:
        return {
            "action": "ASK_CLARIFICATION",
            "booked": False,
            "slot_id": None,
            "spoken_reply": FALLBACK_REPLY,
        }

    action = decision.get("action")
    spoken_reply = decision.get("spoken_reply")
    if action not in _VALID_ACTIONS or not isinstance(spoken_reply, str) or not spoken_reply.strip():
        return {
            "action": "ASK_CLARIFICATION",
            "booked": False,
            "slot_id": None,
            "spoken_reply": FALLBACK_REPLY,
        }

    if action == "BOOK":
        slot_id = decision.get("slot_id")
        allowed_slots = set(open_slots)
        if not isinstance(slot_id, str) or slot_id not in allowed_slots:
            return {
                "action": "ASK_CLARIFICATION",
                "booked": False,
                "slot_id": None,
                "spoken_reply": FALLBACK_REPLY,
            }

        was_booked = await book_slot_fn(customer_id, slot_id)
        if not was_booked:
            return {
                "action": "ASK_CLARIFICATION",
                "booked": False,
                "slot_id": None,
                "spoken_reply": SLOT_CONFLICT_REPLY,
            }

        return {
            "action": "BOOK",
            "booked": True,
            "slot_id": slot_id,
            "spoken_reply": spoken_reply,
        }

    return {
        "action": action,
        "booked": False,
        "slot_id": None,
        "spoken_reply": spoken_reply,
    }
