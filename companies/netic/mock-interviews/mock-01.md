# Mock Interview #1 — Double-Booking Race Condition (45 Minutes)

**Your role:** Candidate  
**AI's role:** Ze Huang, Engineer at Netic  
**Rules:** 45 minutes, Python or TypeScript, AI tools allowed, narrate your thinking out loud.

---

## Candidate Prompt (Read Only This Section During the Mock)

> "Hi Tim, thanks for joining. I'm Ze on Netic's engineering team. Today we'll spend about 35 minutes working through a debugging scenario from an HVAC booking service, leaving 5–10 minutes at the end for your questions. Use any language and AI tools you normally work with — just talk me through your hypotheses and how you're narrowing things down. Ready?"

### Bug Report (`NET-412`)
Homeowners calling to book the final morning HVAC slot occasionally both get told *"You're confirmed for 10:00 AM!"* — leaving two customers expecting the same technician while only the second customer appears on the schedule.

```python
import time

# slot_time -> {"booked": bool, "customer_id": str | None}
schedule = {
    "2026-12-02T10:00": {"booked": False, "customer_id": None},
    "2026-12-02T11:00": {"booked": False, "customer_id": None},
    "2026-12-02T12:00": {"booked": True, "customer_id": "cust_existing"},
}


def is_available(slot_time: str) -> bool:
    slot = schedule.get(slot_time)
    return bool(slot and not slot["booked"])


def book_appointment(slot_time: str, customer_id: str, notify_crm=None) -> bool:
    """
    Book an appointment at slot_time for customer_id.
    Returns True if booked, False if unavailable or unknown slot.
    """
    if not is_available(slot_time):
        return False

    # Simulate CRM validation / network round-trip
    time.sleep(0.05)
    if notify_crm is not None:
        notify_crm(slot_time, customer_id)

    schedule[slot_time]["booked"] = True
    schedule[slot_time]["customer_id"] = customer_id
    return True
```

---

## Interviewer Guide & Rubric (Do Not Read Before Running the Mock)

<details>
<summary>Open Interviewer Script, Progressive Hints & Scorecard</summary>

### Progressive Hints (Only If Stuck)
1. **Minute 4 (no repro yet):** *"Can we write a small test with two concurrent callers hitting `2026-12-02T10:00` so we can watch it fail deterministically?"*
2. **Minute 10 (missed TOCTOU):** *"What happens between `is_available(slot_time)` returning `True` for Caller A and `schedule[slot_time]['booked'] = True` executing 50ms later?"*
3. **Minute 20 (holding global lock across `notify_crm`):** *"Nice — putting a global lock around the whole function stops the double-book. What happens to latency for customers booking 11:00 AM if `notify_crm` takes 2 seconds for 10:00 AM? And what happens if `notify_crm` raises an exception?"*

### Follow-Up Push Questions
- *"If we run 8 uvicorn workers across 3 Kubernetes pods, does `threading.Lock` still prevent double-booking? How do we guarantee atomicity in Postgres?"*
- *"What if the same customer retries their own booking request after a network timeout (idempotency)?"*

### 5-Dimension Scorecard (1–5 Each)
1. **Reproduction Speed:** Built a deterministic concurrent test before patching.
2. **Hypothesis Rigor:** Identified TOCTOU + lock granularity + exception rollback cleanly.
3. **AI Leverage & Verification:** Used AI transparently and verified edge cases (unknown `slot_time`, `notify_crm` failure).
4. **Fix & Test Quality:** Atomic claim/reservation state or per-slot lock; rollback if `notify_crm` raises.
5. **Communication Clarity:** Continuous, structured narration.
</details>
