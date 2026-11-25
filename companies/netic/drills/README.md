# Runnable Blind Debugging Drills (`companies/netic/drills/`)

Four standalone, multi-bug Python mini-services modeled after Netic's production stack.

> **How `drills/` relates to `../exercises/`:**
> - `../exercises/` (`01`–`12`) contains **12 short, self-contained Markdown study cards** (including cross-language React/TypeScript, FastAPI, and SQL snippets) for rapid 15–20 minute pattern recognition.
> - `drills/` (`1`–`4`) is a **separate track of 4 executable, multi-defect Python service labs** with ticket-style docstrings in `problems/` and automated acceptance checks in `checks.py` — built for full IDE + AI debugging simulations with zero `# BUG` spoiler comments.

## Drills Included

| # | File (`problems/`) | Domain | Skills Tested |
|---|--------------------|--------|---------------|
| **1** | `drill_01_slot_scheduler.py` | HVAC Slot Matcher & Reservation Builder | Boundary conditions, mutable state leaks, input validation |
| **2** | `drill_02_async_session_race.py` | Real-Time Async Voice Session & Slot Claim | `asyncio` interleaving races, shared context isolation, rollback on error |
| **3** | `drill_03_webhook_idempotency.py` | CRM Booking Webhook Worker | Distributed retry idempotency, partial-failure safety, failed-attempt recovery |
| **4** | `drill_04_action_gate_harness.py` | Single-LLM Action-Gating Execution Harness | Structured JSON parsing, deterministic guardrail gating, complete action routing |

## How to Practice (Timed Mock Workflow)

1. Pick a drill (`1`–`4`) and run the CLI harness to view the bug ticket and failing checks:
   ```bash
   python3 companies/netic/drills/run_drill.py 1
   ```
2. Open **only** `companies/netic/drills/problems/drill_01_slot_scheduler.py` in your IDE. Start a 25–35 minute timer and narrate your debugging loop out loud.
3. Re-run `python3 companies/netic/drills/run_drill.py 1` until all checks report `PASS`.
4. Only *after* passing (or finishing time), compare your approach with `companies/netic/drills/reference_solutions/`.
   *(Tip: use `but discard companies/netic/drills/problems/` afterwards if you want to reset a drill back to its original buggy state.)*

## Automated Suite Verification

```bash
python3 -m unittest discover -s companies/netic/drills -p "test_*.py" -v
```
