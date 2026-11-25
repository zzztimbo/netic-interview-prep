# My Debugging Playbook (1-Page Cheat Sheet)

## 1. My 5-Step Loop
1. **Reproduce:** Confirm expected vs. actual behavior with a fast failing test/script before editing logic.
2. **Hypothesize Out Loud:** *"Two possibilities are X or Y. X is faster to test via Z."*
3. **Bisect / Isolate:** Log or assert intermediate state halfway through the pipeline to halve the search space.
4. **Minimal Fix:** Fix the broken invariant cleanly — check sibling code paths for the same bug.
5. **Verify & Harden:** Re-run repro + boundary/concurrency tests; name the metric/constraint/eval that prevents recurrence.

## 2. High-Probability Bug Checklist
- [ ] **Concurrency / Async:** Check-then-act gap across `await` / I/O? Missing lock or inconsistent lock acquisition order? Shared module/singleton dict across concurrent requests?
- [ ] **Retries & Idempotency:** Duplicate side effects on webhook/tool retry? Partial write before an exception? Cache invalidated before a failing DB write?
- [ ] **AI / Agent Harness:** Irreversible action (`book`/`cancel`/`refund`) not validated against ground truth? Unvalidated `json.loads` on LLM output? High `temperature` on structured routing?
- [ ] **Data & Boundaries:** Off-by-one (`len - 1`, `<` vs `<=`)? Empty list `[]` vs `None`? Naive local `datetime` mixed with UTC ISO timestamps?
- [ ] **Performance & Contracts:** N+1 query inside loop? Fetching all rows before `[:limit]`? Frontend expecting bare array `[...]` vs `{ items: [...] }` or camelCase vs snake_case?

## 3. My "Stuck" Reset (Never Go Silent)
1. Say: *"That ruled out Hypothesis A — good, that narrows it to [component]."*
2. List **verified facts** vs. **untested assumptions**.
3. Test the **riskiest assumption** next with a 2-line print or unit assertion.

## 4. My AI Collaboration Rules
- **Tell Ze before prompting:** *"I'll ask AI to generate a concurrent test harness while I inspect the lock scope."*
- **Verify every claim:** Run tests and read every changed line; reject `sleep()` hacks or broad refactors.

## 5. Key Netic Context
- **Mission:** AI revenue engine for essential services (>70% Netic-first N1, $43M Series B).
- **Architecture:** Single open-weight LLM + deterministic action-gating execution harness (replaced 223-node graph); ~500ms voice TTFT; 100% reliability bar.
- **Interviewer:** Ze Huang (Netic Eng; ex-VP Eng Poseidon, Founding Eng/Lead Story Protocol, Senior SWE Uber, Verification Eng Marvell).
