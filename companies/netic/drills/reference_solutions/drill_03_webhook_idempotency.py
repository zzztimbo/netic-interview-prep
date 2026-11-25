"""Reference solution for Drill 3: CRM Booking Webhook Worker (Retries & Idempotency)."""

from __future__ import annotations

import asyncio
import json
from typing import Awaitable, Callable


class WebhookBookingWorker:
    def __init__(self) -> None:
        self._results: dict[str, dict] = {}
        self._payload_fingerprints: dict[str, str] = {}
        self._event_locks: dict[str, asyncio.Lock] = {}

    def _fingerprint(self, payload: dict) -> str:
        return json.dumps(payload, sort_keys=True, separators=(",", ":"))

    def _lock_for(self, event_id: str) -> asyncio.Lock:
        lock = self._event_locks.get(event_id)
        if lock is None:
            lock = asyncio.Lock()
            self._event_locks[event_id] = lock
        return lock

    async def handle_event(
        self,
        event_id: str,
        payload: dict,
        dispatch_fn: Callable[[dict], Awaitable[str]],
    ) -> dict:
        fp = self._fingerprint(payload)

        async with self._lock_for(event_id):
            existing_fp = self._payload_fingerprints.get(event_id)
            if existing_fp is not None and existing_fp != fp:
                raise ValueError(
                    f"Idempotency conflict: event_id {event_id!r} reused with different payload"
                )
            self._payload_fingerprints[event_id] = fp

            if event_id in self._results:
                return dict(self._results[event_id])

            try:
                job_id = await dispatch_fn(payload)
            except Exception:
                # Allow legitimate retries with the same payload when dispatch_fn fails
                if event_id not in self._results:
                    self._payload_fingerprints.pop(event_id, None)
                raise

            result = {
                "status": "dispatched",
                "event_id": event_id,
                "job_id": job_id,
            }
            self._results[event_id] = result
            return dict(result)
