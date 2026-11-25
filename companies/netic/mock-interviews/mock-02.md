# Mock Interview #2 — Cross-Call Context Bleed in Async Voice Agent (45 Minutes)

**Your role:** Candidate  
**AI's role:** Ze Huang, Engineer at Netic  
**Rules:** 45 minutes, Python or TypeScript, AI tools allowed, narrate your thinking out loud.

---

## Candidate Prompt (Read Only This Section During the Mock)

> "Hey Tim — for today's session we have an incident from our pest-control voice agent. After a call finishes, our worker writes a call summary to the customer's CRM record. Under concurrent call volume, Customer B's name and address occasionally end up written into Customer A's call summary. Walk me through how you'd reproduce, isolate, and fix this."

### Bug Report (`NET-589`)
Single calls in staging always pass. When two or more calls overlap on the same async worker, `handle_inbound_call` intermittently writes the wrong customer's name/address into `crm_records` AND returns mutated metadata across retries.

```python
import asyncio


class CallSessionManager:
    def __init__(self):
        self._active_session = {
            "call_id": None,
            "customer": None,
            "tags": [],
        }

    def start_session(self, call_id: str, customer: dict) -> dict:
        self._active_session["call_id"] = call_id
        self._active_session["customer"] = customer
        self._active_session["tags"].append("inbound")
        return self._active_session

    async def finalize_call_summary(self, call_id: str, transcript: str, crm_writer) -> dict:
        # Simulate async LLM summarization latency
        await asyncio.sleep(0.05)

        customer = self._active_session["customer"]
        if not customer:
            raise RuntimeError(f"No customer loaded for {call_id}")

        summary = {
            "call_id": call_id,
            "customer_id": customer["id"],
            "customer_name": customer["name"],
            "customer_address": customer["address"],
            "tags": list(self._active_session["tags"]),
            "summary": f"{customer['name']} called regarding: {transcript}",
        }
        await crm_writer(call_id, summary)
        return summary


async def handle_inbound_call(manager: CallSessionManager, call_id: str, customer: dict, transcript: str, crm_writer):
    manager.start_session(call_id, customer)
    return await manager.finalize_call_summary(call_id, transcript, crm_writer)
```

---

## Interviewer Guide & Rubric (Do Not Read Before Running the Mock)

<details>
<summary>Open Interviewer Script, Progressive Hints & Scorecard</summary>

### Hidden Bugs Embedded in This Exercise (Expect Candidate to Find Both!)
1. **Singleton mutable `_active_session` overwritten across `await`:** `CallSessionManager` stores a single `self._active_session` dict on the shared manager instance. While Call A awaits `asyncio.sleep(0.05)` inside `finalize_call_summary`, Call B runs `start_session(...)` on the same event loop and overwrites `self._active_session["customer"]` and `"call_id"`! Call A wakes up and writes Call B's customer under Call A's `call_id`.
2. **Unbounded `"tags"` list accumulation + missing cleanup:** `self._active_session["tags"].append("inbound")` is never reset or scoped per call, so Call #50 gets 50 `"inbound"` tags (and memory leaks if sessions aren't popped after completion).

### Progressive Hints (Only If Stuck)
1. **Minute 5:** *"Write a quick `asyncio.gather` test with Call A and Call B on the same `CallSessionManager` instance and inspect the two returned summaries."*
2. **Minute 12:** *"What happens on the Python event loop when `finalize_call_summary` hits `await asyncio.sleep(0.05)`?"*
3. **Minute 22:** *"Look closely at `tags` across sequential calls too — what happens on the 3rd call even without concurrency, and what happens to memory after 100,000 calls if you key sessions in a dict by `call_id`?"*

### Follow-Up Push Questions
- *"Compare three fixes: (a) keying `self._sessions[call_id]` with `try/finally` cleanup, (b) passing an immutable `CallSession` dataclass / `contextvars.ContextVar` down the call chain, and (c) what breaks if `finalize_call_summary` runs on a separate background Celery/queue worker?"*
</details>
