"""Drill 2: Real-Time Async Voice Session & Slot Claim.

Ticket NET-204:
1. Under concurrent inbound calls on the same worker, Customer A's call summary
   intermittently records Customer B's customer_id and phone number.
2. Two concurrent callers requesting the same open `slot_id` can both receive
   `booked=True`.
3. If `crm_notify` raises a network error during booking, the slot stays permanently
   locked/unavailable even though the booking failed.
"""

from __future__ import annotations

import asyncio
from typing import Awaitable, Callable, Optional


class VoiceBookingCoordinator:
    def __init__(self, open_slots: set[str]) -> None:
        self._open_slots: set[str] = set(open_slots)
        self._bookings: dict[str, str] = {}
        self._current_call: dict[str, Optional[str]] = {
            "call_id": None,
            "customer_id": None,
            "phone": None,
        }

    def begin_call(self, call_id: str, customer_id: str, phone: str) -> None:
        self._current_call["call_id"] = call_id
        self._current_call["customer_id"] = customer_id
        self._current_call["phone"] = phone

    async def process_booking_turn(
        self,
        call_id: str,
        slot_id: str,
        crm_notify: Callable[[str, str], Awaitable[None]],
    ) -> dict:
        if slot_id not in self._open_slots:
            return {
                "call_id": call_id,
                "customer_id": self._current_call["customer_id"],
                "phone": self._current_call["phone"],
                "booked": False,
                "slot_id": slot_id,
            }

        await asyncio.sleep(0.01)
        self._open_slots.remove(slot_id)
        await crm_notify(self._current_call["customer_id"] or "", slot_id)
        self._bookings[slot_id] = self._current_call["customer_id"] or ""

        return {
            "call_id": call_id,
            "customer_id": self._current_call["customer_id"],
            "phone": self._current_call["phone"],
            "booked": True,
            "slot_id": slot_id,
        }

    def get_booked_customer(self, slot_id: str) -> Optional[str]:
        return self._bookings.get(slot_id)

    def is_slot_open(self, slot_id: str) -> bool:
        return slot_id in self._open_slots
