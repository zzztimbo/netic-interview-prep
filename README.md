# netic-interview-prep

Interview preparation repository — tracking companies, roles, study materials, runnable debugging drills, mock interviews, and learning outcomes.

## Active Company Packages

- **[Netic (`companies/netic/`)](companies/netic/01-research-summary.md)** — 45-minute virtual debugging interview with Ze Huang (Wednesday, Dec 2, 2026)
  - [`01-research-summary.md`](companies/netic/01-research-summary.md) — Company architecture, open Ashby roles, Ze Huang profile, and engineering team breakdown
  - [`02-debugging-methodology.md`](companies/netic/02-debugging-methodology.md) — 3-question framework, 6-step debugging loop, out-loud prompts, and AI tool collaboration rules
  - [`03-prep-plan.md`](companies/netic/03-prep-plan.md) — 8-day preparation schedule (Tue Nov 24 → Wed Dec 2, 2026)
  - [`04-interview-day-checklist.md`](companies/netic/04-interview-day-checklist.md) — Pre/during/post interview checklist and questions for Ze
  - [`05-my-playbook.md`](companies/netic/05-my-playbook.md) — 1-page personal notes and cheat-sheet template
  - [`exercises/`](companies/netic/exercises/) — 12 spoiler-free conceptual & code debugging exercises (`01` through `12`)
  - [`mock-interviews/`](companies/netic/mock-interviews/) — 3 structured 45-minute interviewer scripts (`mock-01` through `mock-03`)
  - [`drills/`](companies/netic/drills/README.md) — 4 runnable, spoiler-free Python debugging mini-services + automated test runner

## Quick Start: Runnable Debugging Drills

```bash
# Run a specific candidate drill (1-4) to see failing symptom checks:
python3 companies/netic/drills/run_drill.py 1

# Verify all drill reproductions + reference solutions:
python3 -m unittest discover -s companies/netic/drills -p "test_*.py" -v
```
