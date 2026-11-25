# Exercise 9: Conversation State Machine Fallthrough (Medium–Hard)

## Scenario
Netic's legacy call router tracks turn state across a phone call:
```
GREETING → INTENT_CHECK → EMERGENCY_CHECK → COLLECT_INFO → CONFIRM → BOOKED
                        ↘ CANCELLATION → CANCELLED
```
Callers who say *"I need to cancel my appointment"* get routed to *"What type of service do you need?"* (the booking `COLLECT_INFO` prompt) on their very next turn instead of entering the cancellation flow.

## Candidate Code
```python
class BookingStateMachine:
    def __init__(self):
        self.state = "GREETING"
        self.context = {}

    def _classify_intent(self, text: str) -> str:
        lowered = text.lower()
        if "cancel" in lowered:
            return "CANCEL"
        if "book" in lowered or "schedule" in lowered:
            return "BOOK"
        return "UNKNOWN"

    def step(self, user_text: str) -> str:
        if self.state == "GREETING":
            self.state = "INTENT_CHECK"
            return "Thanks for calling! How can I help you today?"

        if self.state == "INTENT_CHECK":
            intent = self._classify_intent(user_text)
            if intent == "BOOK":
                self.state = "EMERGENCY_CHECK"
                return "Is this an urgent emergency?"
            if intent == "CANCEL":
                self.state = "CANCELLATION"

        if self.state == "EMERGENCY_CHECK":
            self.context["is_emergency"] = "yes" in user_text.lower()
            self.state = "COLLECT_INFO"
            return "What type of service do you need?"

        if self.state == "COLLECT_INFO":
            self.context["service"] = user_text
            self.state = "CONFIRM"
            return f"Confirming {user_text} — should I lock that in?"

        self.state = "COLLECT_INFO"
        return "What type of service do you need?"
```

## Your Task (25 min)
1. Trace `step()` across Turn 1 (`"Hi"`) and Turn 2 (`"I need to cancel my appointment"`) line-by-line to explain why it asks *"What type of service do you need?"*.
2. Identify all structural state-machine flaws (`if` vs `elif` fallthrough, missing `CANCELLATION` handler, silent catch-all mutating `self.state = "COLLECT_INFO"`, and `UNKNOWN` intent handling).
3. Refactor cleanly using `Enum` states and explicit transition handlers, and explain why Netic replaced a 223-node state graph with a single LLM + deterministic action-gating harness.

<details>
<summary>Root Cause & Reference Fix (Open After Attempting)</summary>

- **Root causes:**
  1. **Missing `return` + sequential `if` blocks + dangerous catch-all:** When `intent == "CANCEL"`, `self.state` is set to `"CANCELLATION"` without returning. Execution falls past `EMERGENCY_CHECK` and `COLLECT_INFO` straight into the trailing fallback, which overwrites `self.state = "COLLECT_INFO"` and asks *"What type of service do you need?"*!
  2. **`UNKNOWN` intent does the same thing:** Saying *"What are your hours?"* also falls through into `COLLECT_INFO` instead of re-prompting or answering.
- **Fix:** Use `elif` / `match self.state:` with an `Enum`, implement explicit `CANCELLATION -> CANCELLED` confirmation + gating, re-prompt on `UNKNOWN`, and raise/log on unreachable states instead of silently coercing state.
</details>
