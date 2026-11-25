"""Drill 3: CRM Booking Webhook Worker (Retries & Idempotency).

Ticket NET-318:
1. When an upstream CRM webhook times out on its side and re-delivers the exact same
   `event_id` with identical payload, `WebhookBookingWorker.handle_event` dispatches
   a duplicate technician job if called concurrently, OR drops valid retries when
   `dispatch_fn` raised a transient error on the first attempt!
2. If the same `event_id` arrives with a *different* payload (e.g. forged or corrupted
   event key reuse), the worker silently returns success instead of raising ValueError.
"""

from __future__ import annotations

import asyncio
import json
from typing import Awaitable, Callable


class WebhookBookingWorker:
    def __init__(self) -> None:
        self._processed_events: set[str] = set()
        self._results: dict[str, dict] = {}

    async def handle_event(
        self,
        event_id: str,
        payload: dict,
        dispatch_fn: Callable[[dict], Awaitable[str]],
    ) -> dict:
        if event_id in self._processed_events:
            return self._results.get(event_id, {"status": "duplicate", "job_id": None})

        # Mark seen before awaiting external dispatch
        self._processed_events.add(event_id)
        _ = json.dumps(payload, sort_keys=True)

        job_id = await dispatch_fn(payload)
        result = {"status": "dispatched", "event_id": event_id, "job_id": job_id}
        self._results[event_id] = result
        return result
