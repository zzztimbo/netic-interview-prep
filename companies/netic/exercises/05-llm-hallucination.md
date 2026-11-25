# Exercise 5: LLM Slot Hallucination & Ungated Action (Medium–Hard)

## Scenario
Netic's voice agent answers customer questions about HVAC availability and books requested slots. Customers report that roughly 3% of the time the agent offers and attempts to book a time like `"Tuesday at 3:00 PM"` that does not exist in `available_slots`, or echoes a time from the customer's *past* service history as if it were an open future slot.

## Candidate Code
```python
import json


def build_prompt(customer_history, available_slots, question):
    return f"""You are Netic's AI scheduling assistant.

Customer history:
{json.dumps(customer_history)}

Available slots:
{json.dumps(available_slots)}

Customer said: {question}

Reply with helpful availability and, if they asked to book, include JSON on the last line:
{{"book_slot": "<slot_iso>"}}"""


def handle_turn(customer_id, question, crm_api, slots_api, llm_call):
    history = crm_api.get_history(customer_id)
    open_slots = slots_api.get_available_slots()
    prompt = build_prompt(history, open_slots, question)
    raw = llm_call(prompt, model="open-llm-70b", temperature=0.7)

    if '{"book_slot"' in raw:
        json_line = raw.strip().splitlines()[-1]
        payload = json.loads(json_line)
        slots_api.book(customer_id, payload["book_slot"])

    return raw
```

## Your Task (20 min)
1. Identify **all** failure modes across prompt construction, sampling parameters, output parsing, and action execution.
2. Design a deterministic **action-gating check** (mirroring Netic's production execution harness) so an invented or historical timestamp can *never* reach `slots_api.book`.
3. Explain how you would write offline regression evals and production monitors for this flow.

<details>
<summary>Root Cause & Reference Fix (Open After Attempting)</summary>

- **Root causes:**
  1. **No deterministic action gate:** `payload["book_slot"]` is passed straight to `slots_api.book(...)` without verifying `slot_iso in valid_open_slot_ids`.
  2. **High sampling temperature (`0.7`) + brittle free-text JSON scraping:** `splitlines()[-1]` breaks if the model adds trailing text or markdown fences.
  3. **Context pollution:** Dumping unbounded `customer_history` with timestamps next to `available_slots` confuses attention when `open_slots` is empty or sparse.
- **Fix:** Use `temperature=0` + structured tool/JSON schema output, summarize/scope history fields, parse defensively with `try/except`, and **gate** `slots_api.book` against the exact server-side `open_slots` set before executing.
</details>
