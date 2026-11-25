"""Reference solution for Drill 2: Real-Time Async Voice Session & Slot Claim."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Awaitable, Callable, Optional


@dataclass(frozen=True)
class CallSession:
    call_id: str
    customer_id: str
    phone: str


class VoiceBookingCoordinator:
    def __init__(self, open_slots: set[str]) -> None:
        self._open_slots: set[str] = set(open_slots)
        self._pending_slots: set[str] = set()
        self._bookings: dict[str, str] = {}
        self._sessions: dict[str, CallSession] = {}
        self._slot_locks: dict[str, asyncio.Lock] = {}

    def begin_call(self, call_id: str, customer_id: str, phone: str) -> None:
        self._sessions[call_id] = CallSession(
            call_id=call_id,
            customer_id=customer_id,
            phone=phone,
        )

    def _get_slot_lock(self, slot_id: str) -> asyncio.Lock:
        lock = self._slot_locks.get(slot_id)
        if lock is None:
            lock = asyncio.Lock()
            self._slot_locks[slot_id] = lock
        return lock

    async def process_booking_turn(
        self,
        call_id: str,
        slot_id: str,
        crm_notify: Callable[[str, str], Awaitable[None]],
    ) -> dict:
        session = self._sessions.get(call_id)
        if session is None:
            raise KeyError(f"Unknown call_id: {call_id}")

        async with self._get_slot_lock(slot_id):
            if slot_id not in self._open_slots or slot_id in self._pending_slots:
                return {
                    "call_id": session.call_id,
                    "customer_id": session.customer_id,
                    "phone": session.phone,
                    "booked": False,
                    "slot_id": slot_id,
                }
            # Reserve slot atomically before yielding to external I/O
            self._open_slots.remove(slot_id)
            self._pending_slots.add(slot_id)

        try:
            await asyncio.sleep(0.01)
            await crm_notify(session.customer_id, slot_id)
        except Exception:
            async with self._get_slot_lock(slot_id):
                self._pending_slots.discard(slot_id)
                self._open_slots.add(slot_id)
            raise
        else:
            async with self._get_slot_lock(slot_id):
                self._pending_slots.discard(slot_id)
                self._bookings[slot_id] = session.customer_id

        return {
            "call_id": session.call_id,
            "customer_id": session.customer_id,
            "phone": session.phone,
            "booked": True,
            "slot_id": slot_id,
        }

    def get_booked_customer(self, slot_id: str) -> Optional[str]:
        return self._bookings.get(slot_id)

    def is_slot_open(self, slot_id: str) -> bool:
        return slot_id in self._open_slots
