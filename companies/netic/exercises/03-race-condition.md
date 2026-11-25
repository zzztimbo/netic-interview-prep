# Exercise 3: Check-Then-Act Booking Race Condition (Medium)

## Scenario
Two homeowners call simultaneously requesting the last 10:00 AM plumbing slot. Both receive spoken confirmation that their appointment is booked, overwriting the first customer's reservation.

## Candidate Code
```python
import threading
import time

slots = {"2026-12-15T10:00": {"available": True, "customer": None}}
lock = threading.Lock()


def book_slot(slot_time, customer_id):
    if slots[slot_time]["available"]:
        time.sleep(0.05)  # Simulate external validation / I/O
        slots[slot_time]["available"] = False
        slots[slot_time]["customer"] = customer_id
        return True
    return False
```

## Your Task (20 min)
1. Write a multithreaded reproduction proving both callers get `True` while one customer's booking is silently lost.
2. Walk through the exact TOCTOU (time-of-check to time-of-use) interleaving.
3. Fix the synchronization cleanly without holding a global lock across slow external network I/O.
4. Answer Ze's follow-ups:
   - Why doesn't an in-process `threading.Lock()` protect multi-worker FastAPI/Gunicorn deployments?
   - How would you enforce single-winner booking in Postgres (`SELECT ... FOR UPDATE`, atomic `UPDATE ... WHERE available = true`, or unique constraint)?

<details>
<summary>Root Cause & Reference Fix (Open After Attempting)</summary>

- **Root cause:** `lock` is defined but never acquired, and the check (`slots[slot_time]["available"]`) is separated from the mutation by `time.sleep(0.05)`.
- **Minimal fix:** Acquire per-slot (or guarded state) lock around an atomic claim/reservation state (`PENDING` -> external I/O -> `BOOKED` or rollback on failure), and in production rely on an atomic Postgres `UPDATE slots SET available = false, customer_id = $1 WHERE slot_time = $2 AND available = true RETURNING *`.
</details>
