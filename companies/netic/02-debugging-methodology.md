# Debugging Methodology — The Framework

## The Core Insight

Ze isn't testing whether you already know where the bug is. He's testing **how you get to the root cause**. When AI tools are allowed, syntax recall is free — your **engineering judgment, hypothesis discipline, and verbal clarity** are the entire signal.

---

## The 3-Question Framework

Run this mental check on every bug:

1. **"What did I expect vs. what actually happened?"**
   - State the expected invariant and actual behavior explicitly. The gap *is* the bug.
2. **"What assumptions must fail for that gap to happen?"**
   - Data shape? Ordering/concurrency? Cache/state lifecycle? Boundary condition? Recent deploy/job?
3. **"What is the smallest test or probe that proves or disproves my top hypothesis?"**
   - Never edit production logic to "see if it fixes it." Reproduce first, bisect second, patch third.

---

## The 45-Minute Debugging Loop (Pacing Guide)

```
┌──────────────────────────────────────────────────────────────────┐
│  1. ORIENT & REPRODUCE (Minutes 0–6)                             │
│     Read problem/logs/tests first. Run existing tests or build   │
│     a deterministic repro script (red test) before editing code. │
├──────────────────────────────────────────────────────────────────┤
│  2. ISOLATE & HYPOTHESIZE (Minutes 6–16)                         │
│     State 2–3 concrete hypotheses out loud. Bisect the data flow │
│     with targeted logs, assertions, or minimal inputs.           │
├──────────────────────────────────────────────────────────────────┤
│  3. VERIFY TRUE ROOT CAUSE (Minutes 16–26)                       │
│     Pinpoint the exact broken invariant — not just a symptom.    │
│     Check sibling code paths for the same class of bug.          │
├──────────────────────────────────────────────────────────────────┤
│  4. MINIMAL FIX + REGRESSION TEST (Minutes 26–38)                │
│     Apply a focused, readable fix. Confirm your red repro test   │
│     turns green and all existing tests + edge cases pass.        │
├──────────────────────────────────────────────────────────────────┤
│  5. PRODUCTION HARDENING & Q&A (Minutes 38–45)                   │
│     State what observability (Datadog metrics/traces), DB        │
│     constraints, or guardrails would catch/prevent this at scale.│
└──────────────────────────────────────────────────────────────────┘
```

---

## Talking Out Loud — Phrase Templates

- **Opening:** *"Let me restate the symptom to make sure I have the invariant right: we expect X, we're seeing Y. Before changing anything, I want to reproduce that reliably."*
- **Forming hypotheses:** *"Two things could cause this symptom: (1) [Hypothesis A] or (2) [Hypothesis B]. Hypothesis A is faster to rule in/out, so I'll check [line/input] first."*
- **Adding a probe:** *"I'm logging `[variable]` right before `[call]`. If it's already wrong here, the bug is upstream; if it's clean here, the bug happens inside or after `[call]`."*
- **Before fixing:** *"Okay, confirmed — the root cause is [exact mechanism]. Let me check if any sibling function makes the same assumption before I patch it."*
- **When stuck:** *"That ruled out Hypothesis A, which narrows the fault to [remaining component]. Let me list what we know is true vs. what I haven't verified yet."*

---

## Smart AI Tool Usage (Strong Hire vs. No-Hire)

| Strong Hire Signal | No-Hire Trap |
|--------------------|--------------|
| Use AI to **map unfamiliar files quickly** (*"List every place `active_sessions` is written or deleted"*) | Dumping the whole prompt into AI and saying *"fix this"* before reading the code yourself |
| Use AI to **generate a concurrency/boundary repro test** while explaining your test plan to Ze | Going silent for 2 minutes while reading long AI completions |
| **Verify and critique** AI suggestions (*"AI suggested adding a retry, but without an idempotency key that worsens duplicate writes"*) | Applying a broad AI refactor or `sleep()` band-aid you can't justify line-by-line |

---

## Netic-Specific Bug Checklists

### 1. Async, Concurrency & Distributed State
- Is there an `await` or I/O call between checking a condition and mutating state (TOCTOU race)?
- Are locks acquired in inconsistent order across two operations (deadlock)?
- Is request/call context stored in module-level or singleton mutable state shared across concurrent tasks?
- If a webhook or tool call times out and retries, is the handler idempotent?

### 2. AI / LLM / Agent Harness Bugs
- Is irreversible action execution (`book`, `cancel`, `refund`) gated by deterministic code validation against ground truth (`available_slots`), or trusting raw LLM text/JSON?
- Is structured output enforced (schema validation + `temperature=0` + error handling on malformed JSON)?
- Did context truncation or prompt construction drop critical guardrails or pollute customer context?

### 3. Data, Caching & Latency
- Does every write/delete path invalidate or update cached reads? And what happens if the DB write fails?
- Are queries running inside a loop (N+1) or fetching unbounded rows before slicing `[:limit]` in Python?
- Are timestamps timezone-aware UTC end-to-end, or mixing naive `datetime.now()` with UTC ISO strings?
- Are per-stage latency spans logged (`stt`, `llm`, `crm`, `booking`, `tts`) so bottlenecks are observable?
