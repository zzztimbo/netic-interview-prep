# Interview Day Checklist — Wednesday, Dec 2, 2026

## 24 Hours Before (Tue Dec 1)

- [ ] Test camera, microphone, internet connection, and screen-sharing permissions in Zoom/Google Meet
- [ ] Open a clean workspace in your preferred IDE with Python (`pytest`/`unittest`) and/or TypeScript (`tsx`/`vitest`) ready to run in one shortcut
- [ ] Configure your AI assistant (Cursor / Claude Code / Copilot / ChatGPT) and close unrelated noisy projects
- [ ] Review `01-research-summary.md` and your 1-page `05-my-playbook.md`
- [ ] Finalize 3–4 tailored questions for Ze (examples below)
- [ ] Get a full night's sleep

## 1 Hour Before

- [ ] Eat a light meal and have water nearby
- [ ] Scan your 1-page `05-my-playbook.md` (5-step loop + out-loud transitions)
- [ ] Run a 2-minute sanity check in your terminal (`python3 --version`, test runner works)
- [ ] Silence phone & desktop notifications; close extra browser tabs

## 10 Minutes Before

- [ ] Join the link 2–3 minutes early; verify audio/video
- [ ] Take 3 slow breaths
- [ ] Keep one anchor in mind: **Reproduce → Hypothesize out loud → Smallest probe → Minimal fix → Verify & harden**

---

## During the 45-Minute Interview

### Minutes 0–5: Warm Intro & Clarify Invariants
- [ ] Greet Ze warmly; briefly connect your background to building reliable production systems
- [ ] Read the prompt/code/logs carefully before touching the keyboard
- [ ] Restate expected vs. actual behavior and ask 1–2 clarifying questions (concurrency model, scale, input guarantees)

### Minutes 5–35: Scientific Debugging Loop
- [ ] **Narrate continuously** — never go silent for more than 15–20 seconds
- [ ] **Reproduce first** — run the failing case or write a 5-line repro test before editing production code
- [ ] **State hypotheses before probing** (*"I suspect X because Y; I'll check Z to confirm"*)
- [ ] **Use AI with discipline** — tell Ze what you're asking AI, verify its output against the code, and reject band-aids
- [ ] **Check sibling paths & edge cases** — empty/null inputs, timezone boundaries, concurrent requests, error/retry paths

### Minutes 35–45: Verify, Harden & Ask Sharp Questions
- [ ] Run the repro test + edge-case checks to prove the fix works without regressions
- [ ] Briefly note production hardening (metrics/traces in Datadog, idempotency keys, DB constraints, regression evals)
- [ ] Ask Ze 2–3 thoughtful engineering questions

---

## High-Signal Questions to Ask Ze

1. *"I read about Netic replacing the 223-node agent graph with a single open-weight LLM plus an action-gating execution harness. From a systems/verification standpoint, what have been the hardest failure modes to catch before an irreversible action fires?"*
2. *"With >70% of customers running Netic-first 24/7 and voice TTFT targets around 500ms, how does the team structure observability and incident triage when latency spikes or an upstream provider degrades?"*
3. *"Having built high-spike and verification-heavy systems at Uber and Story Protocol before joining Netic, what surprised you most about the engineering challenges here?"*
4. *"What distinguishes an engineer who ramps fastest in their first 60 days on your team?"*

---

## Emergency Recovery Playbook

| Situation | Exact Move |
|-----------|------------|
| **You blank out** | *"Let me step back to the invariant: we expect X and get Y. Let me trace the input from entry point to output and check each transformation."* |
| **Bug won't reproduce** | *"Deterministic inputs pass, which points toward timing/concurrency, shared mutable state, or environment/clock assumptions. Let me test concurrent calls and boundary timestamps."* |
| **AI gives a wrong/hacky fix** | *"That suggestion masks the symptom rather than fixing why state diverged. Let me check the underlying lifecycle instead."* |
| **5 minutes left without full patch** | Summarize clearly: (1) what hypotheses you ruled out, (2) exact narrowed fault region, (3) minimal fix you'd apply, and (4) the test/metric that proves it. |

## After the Interview
- [ ] Send a concise thank-you note to Omar Elbadrawy (and Ze) within 2–4 hours referencing a specific technical detail from your conversation
- [ ] Jot down 3 takeaways while fresh
