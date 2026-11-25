# Mock Interview #3 — Dress Rehearsal: Voice Agent Execution Harness (45 Minutes)

**Your role:** Candidate  
**AI's role:** Ze Huang, Engineer at Netic  
**Rules:** Full dress rehearsal — 45 minutes, camera/screen-share mindset, AI tools allowed, narrate continuously.

---

## Candidate Prompt (Read Only This Section During the Mock)

> "Hi Tim — welcome to the session. Here is a simplified slice of an appointment-routing harness for a voice agent. In production we're seeing three customer-impacting issues:
> 1. Roughly 2% of calls crash with an unhandled `JSONDecodeError` or `KeyError`.
> 2. Occasionally the agent books a slot ID that was already taken or never offered.
> 3. When a caller doesn't give enough detail yet (so the LLM responds with `ASK_MORE`), the caller hears dead air instead of the follow-up question.
>
> Walk me through how you'd reproduce, diagnose, and harden this."

### Candidate Code
```python
import json


async def handle_customer_turn(
    audio_stream,
    session_id: str,
    stt,
    context_store,
    slots_service,
    llm,
    tts,
):
    transcript = await stt.transcribe(audio_stream)
    context = await context_store.load(session_id)
    open_slots = await slots_service.list_open_slots(context["business_id"])

    raw_response = await llm.generate(
        prompt=f"""
Context: {json.dumps(context)}
Open slots: {json.dumps(open_slots)}
Customer said: {transcript}

Choose action BOOK, CANCEL, or ASK_MORE.
Respond with JSON: {{"action": "...", "slot_id": "...", "spoken_reply": "..."}}
""",
        temperature=0.7,
    )

    decision = json.loads(raw_response)

    if decision["action"] == "BOOK":
        await slots_service.book(context["customer_id"], decision["slot_id"])
        return await tts.synthesize(decision["spoken_reply"])
    elif decision["action"] == "CANCEL":
        await slots_service.cancel(context["customer_id"], decision["slot_id"])
        return await tts.synthesize(decision["spoken_reply"])
```

---

## Interviewer Guide & Rubric (Do Not Read Before Running the Mock)

<details>
<summary>Open Interviewer Script, Progressive Hints & Scorecard</summary>

### Defects to Expect the Candidate to Uncover & Fix
1. **Dead air on `ASK_MORE` (and unknown actions):** `if/elif` only handles `BOOK` and `CANCEL` and implicitly returns `None` when `decision["action"] == "ASK_MORE"` — never calling `tts.synthesize(decision["spoken_reply"])`!
2. **Crash on malformed LLM output / Markdown code fences / missing keys:** `json.loads(raw_response)` crashes if the LLM wraps JSON in ```` ```json ... ``` ```` or omits `"slot_id"`/`"spoken_reply"`, compounded by `temperature=0.7` on structured decision routing.
3. **Ungated irreversible action (`slots_service.book` / `cancel`):** Passes `decision["slot_id"]` straight to `slots_service.book` without checking that `slot_id` is actually in `open_slots` (and checking `slots_service.book` return status before synthesizing *"You're booked!"* if another caller just took it!).

### Interviewer Pushbacks
- If candidate only lowers `temperature=0`: *"Good, that lowers variance, but can an LLM at `temperature=0` still hallucinate a `slot_id` or return invalid JSON on adversarial speech transcripts? How do we guarantee safety in code?"*
- If candidate validates `slot_id in open_slot_ids`: *"What if `slot_id` was in `open_slots` 400ms ago before `llm.generate`, and another call booked it while the LLM was thinking? What should happen if `slots_service.book` returns `False`?"*
- At Minute 35: *"Let's make sure your tests cover all three bug reports, then tell me what regression evals and Datadog metrics you'd ship alongside this PR."*
</details>
