# 8-Day Prep Plan: Tue Nov 24 → Wed Dec 2, 2026

Your interview is **Wednesday, December 2, 2026**. Today is **Tuesday, November 24, 2026** — giving you 8 full prep days.

Format: 45-minute virtual **debugging** interview with Ze Huang (Netic senior engineer). Not LeetCode. Any language. AI tools allowed. Think out loud.

## Daily Schedule Overview (60–90 min/day)

| Day | Date | Focus | Exercises & Runnable Drills |
|-----|------|-------|-----------------------------|
| **Day 1** | **Tue Nov 24** (today) | Baseline setup + methodology + boundary bugs | Read `01` & `02`; Ex `01` (off-by-one); Runnable **Drill #1** (`run_drill.py 1`) |
| **Day 2** | **Wed Nov 25** | Caching + async/concurrency races | Ex `02` (stale cache), Ex `03` (race condition); Runnable **Drill #2** (`run_drill.py 2`) |
| **Day 3** | **Thu Nov 26** | **Thanksgiving Day** — light review | Review notes, customize `05-my-playbook.md` (no heavy coding needed) |
| **Day 4** | **Fri Nov 27** | Distributed webhooks, idempotency & deadlocks | Ex `07` (deadlock), Ex `10` (5am prod incident); Runnable **Drill #3** (`run_drill.py 3`) |
| **Day 5** | **Sat Nov 28** | **Mock Interview #1** + AI/LLM agent harness | Timed 45-min `mock-01.md`; Ex `05` (LLM hallucination); Runnable **Drill #4** (`run_drill.py 4`) |
| **Day 6** | **Sun Nov 29** | Full-stack contracts, DB perf & state machines | Ex `04` (API mismatch), Ex `06` (slow query), Ex `08` (full-stack state), Ex `09` (state machine) |
| **Day 7** | **Mon Nov 30** | **Mock Interview #2** + observability & AI workflow | Timed 45-min `mock-02.md`; Ex `11` (AI-assisted), Ex `12` (distributed tracing) |
| **Day 8** | **Tue Dec 1** | **Mock Interview #3 (Dress Rehearsal)** + final check | Timed 45-min `mock-03.md`; review `04-interview-day-checklist.md`; rest early |
| **—** | **Wed Dec 2** | **INTERVIEW DAY** | Light 10-min playbook scan, tech check, execute calmly |

---

## Day-by-Day Action Checklist

### Day 1 (Tue Nov 24) — Setup, Narration Habit & Boundary Bugs
- [ ] Read `01-research-summary.md` and `02-debugging-methodology.md`
- [ ] Confirm your interview language (Python or TypeScript) and live AI setup (Cursor, Claude Code, Copilot, or ChatGPT)
- [ ] Complete `exercises/01-off-by-one.md` while narrating every step out loud
- [ ] Run and fix **Runnable Drill #1** (`companies/netic/drills/problems/drill_01_slot_scheduler.py`) using `python3 companies/netic/drills/run_drill.py 1`

### Day 2 (Wed Nov 25) — Stale Caches & Async Concurrency
- [ ] Complete `exercises/02-stale-cache.md` and `exercises/03-race-condition.md`
- [ ] Run and fix **Runnable Drill #2** (`drill_02_async_session_race.py`) — practice writing a deterministic async reproduction before touching the code

### Day 3 (Thu Nov 26) — Thanksgiving (Light Day)
- [ ] Fill out `05-my-playbook.md` in your own words (your go-to opening lines, stuck protocol, and AI verification rules)
- [ ] Draft 3 crisp 60–90s STAR stories (production incident/root cause, rapid adaptation, owning an end-to-end customer problem)

### Day 4 (Fri Nov 27) — Retries, Idempotency, Deadlocks & Incidents
- [ ] Complete `exercises/07-deadlock.md` and `exercises/10-prod-incident.md`
- [ ] Run and fix **Runnable Drill #3** (`drill_03_webhook_idempotency.py`) — Ze's distributed-systems sweet spot

### Day 5 (Sat Nov 28) — Mock Interview #1 + Netic Agent Harness
- [ ] Run a strict 45-minute timed session on `mock-interviews/mock-01.md` (AI plays Ze)
- [ ] Complete `exercises/05-llm-hallucination.md`
- [ ] Run and fix **Runnable Drill #4** (`drill_04_action_gate_harness.py`) — LLM tool-call gating & guardrail invariants

### Day 6 (Sun Nov 29) — Full-Stack Contracts, DB Queries & State Machines
- [ ] Complete `exercises/04-api-mismatch.md` and `exercises/08-frontend-backend.md`
- [ ] Complete `exercises/06-slow-query.md` and `exercises/09-state-machine.md`
- [ ] Re-solve any weak spot surfaced in Mock #1

### Day 7 (Mon Nov 30) — Mock Interview #2 + Observability & AI Workflow
- [ ] Run a strict 45-minute timed session on `mock-interviews/mock-02.md`
- [ ] Complete `exercises/11-ai-assisted.md` and `exercises/12-distributed-tracing.md`

### Day 8 (Tue Dec 1) — Dress Rehearsal & Tech Check
- [ ] Run `mock-interviews/mock-03.md` under exact interview conditions (camera, mic, screen share, editor, AI tool)
- [ ] Walk through `04-interview-day-checklist.md` and finalize 3–4 sharp questions for Ze
- [ ] Close prep early and get a full night's sleep

### Interview Day (Wed Dec 2)
- [ ] Follow `04-interview-day-checklist.md`
- [ ] Reproduce first, state hypotheses before testing, verify AI outputs, and narrate clearly throughout
