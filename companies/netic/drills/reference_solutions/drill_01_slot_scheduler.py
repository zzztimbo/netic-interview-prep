"""Reference solution for Drill 1: HVAC Slot Matcher & Reservation Builder."""

from __future__ import annotations

from datetime import datetime
from typing import Optional


def _ensure_tz_aware(dt: datetime, label: str) -> None:
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        raise ValueError(f"{label} must be timezone-aware, got naive datetime {dt!r}")


def find_earliest_slot(
    available_slots: list[datetime],
    preferred_time: datetime,
) -> Optional[datetime]:
    """Return the earliest slot >= preferred_time, or None if none qualify.

    Raises ValueError if preferred_time or any slot is timezone-naive.
    """
    _ensure_tz_aware(preferred_time, "preferred_time")
    for slot in available_slots:
        _ensure_tz_aware(slot, "available_slots item")

    candidates = [slot for slot in available_slots if slot >= preferred_time]
    if not candidates:
        return None
    return min(candidates)


def build_reservation(
    customer_id: str,
    slot_time: datetime,
    is_emergency: bool = False,
    tags: Optional[list[str]] = None,
) -> dict:
    """Create a reservation payload without mutating caller or default lists."""
    _ensure_tz_aware(slot_time, "slot_time")
    safe_tags = list(tags) if tags is not None else []
    if is_emergency and "emergency" not in safe_tags:
        safe_tags.append("emergency")

    return {
        "customer_id": customer_id,
        "slot_time": slot_time.isoformat(),
        "is_emergency": is_emergency,
        "tags": safe_tags,
    }
