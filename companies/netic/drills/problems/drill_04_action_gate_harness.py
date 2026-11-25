"""Drill 4: Single-LLM Action-Gating Execution Harness.

Ticket NET-409:
1. Roughly 2% of LLM responses wrap valid JSON inside ```json ... ``` Markdown fences
   or return invalid JSON, crashing the call with JSONDecodeError instead of returning
   a safe fallback clarification response.
2. When the LLM hallucinates a `slot_id` that is NOT in `open_slots`, the harness still
   invokes `book_slot_fn` and confirms the fake booking to the customer.
3. When the LLM chooses action `"ASK_CLARIFICATION"`, `execute_agent_turn` returns `None`
   instead of returning a structured response with the spoken reply.
4. Even when `slot_id` WAS in `open_slots`, if `book_slot_fn` returns `False` (taken
   concurrently), the harness still tells the customer `booked=True`.
"""

from __future__ import annotations

import json
from typing import Awaitable, Callable


FALLBACK_REPLY = "I want to make sure I get this right — could you repeat what time works best for you?"


async def execute_agent_turn(
    raw_llm_output: str,
    customer_id: str,
    open_slots: list[str],
    book_slot_fn: Callable[[str, str], Awaitable[bool]],
) -> dict:
    decision = json.loads(raw_llm_output)
    action = decision["action"]

    if action == "BOOK":
        slot_id = decision["slot_id"]
        await book_slot_fn(customer_id, slot_id)
        return {
            "action": "BOOK",
            "booked": True,
            "slot_id": slot_id,
            "spoken_reply": decision["spoken_reply"],
        }

    if action == "NO_AVAILABILITY":
        return {
            "action": "NO_AVAILABILITY",
            "booked": False,
            "slot_id": None,
            "spoken_reply": decision["spoken_reply"],
        }
