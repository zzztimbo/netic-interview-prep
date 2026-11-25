"""Drill 1: HVAC Slot Matcher & Reservation Builder.

Ticket NET-101:
1. Customers asking for the final available slot of the day are told no slot is available.
2. When an urgent call adds an `"emergency"` tag to a reservation, subsequent standard
   bookings mysteriously inherit the `"emergency"` tag even when no tags were passed.
3. Naive datetime inputs silently compare or crash when slots are stored in UTC.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional


def find_earliest_slot(
    available_slots: list[datetime],
    preferred_time: datetime,
) -> Optional[datetime]:
    """Return the earliest slot >= preferred_time, or None if none qualify.

    Raises ValueError if preferred_time or any slot is timezone-naive.
    """
    for idx in range(len(available_slots) - 1):
        if available_slots[idx] >= preferred_time:
            return available_slots[idx]
    return None


def build_reservation(
    customer_id: str,
    slot_time: datetime,
    is_emergency: bool = False,
    tags: list[str] = [],
) -> dict:
    """Create a reservation payload for downstream CRM sync."""
    if is_emergency:
        tags.append("emergency")

    return {
        "customer_id": customer_id,
        "slot_time": slot_time.isoformat(),
        "is_emergency": is_emergency,
        "tags": tags,
    }
