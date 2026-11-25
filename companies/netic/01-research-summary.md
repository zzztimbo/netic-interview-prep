# Netic Debugging Interview Research — Wed Dec 2, 2026

## 1. Snapshot

| Attribute | Detail |
|-----------|--------|
| **Company** | Netic (`netic.ai`, Cybernetic Labs Inc.) — AI revenue engine for essential service enterprises (HVAC, plumbing, electrical, pest control, roofing, veterinary, automotive, wellness) |
| **Scale & Funding** | $43M total raised — Series B led by Founders Fund, with Greylock, Hanabi, Day One Ventures; angels include Dylan Field (Figma CEO), Alexandr Wang (Scale AI CEO), Elad Gil. >70% of customers run **"Netic-first (N1)"** (autonomous multimodal voice/SMS/web agents handling first contact 24/7) |
| **Founder** | Melisa Tokmak (Stanford, ex-Scale AI GM of Government & Enterprise) |
| **Team Size** | ~70 employees total; ~23–25 engineers |
| **Interviewer** | **Ze Huang** — Senior/Staff-level Engineer at Netic (joined July 2026, SF Bay Area) |
| **Recruiter** | Omar Elbadrawy |
| **Format** | 45-minute virtual **debugging** interview — **not** LeetCode-style |
| **Rules** | Use your strongest language (Python or TypeScript recommended); **AI tools allowed**; **talk Ze through your thinking out loud** |

---

## 2. Netic's Architecture & Engineering DNA (From Engineering Blog)

Understanding what Netic runs in production explains why they test real-world debugging instead of algorithm puzzles:

1. **Single-LLM Execution Harness (Replaced 223-Node Graph):**
   - Netic migrated away from a brittle 223-node multi-agent graph (which suffered from handoff bugs, state loss, and looping) to a **single open-weight LLM** wrapped in a **proprietary execution harness**.
   - The harness dynamically loads operating procedures into context, **gates every irreversible action** (appointment booking, CRM writes, technician dispatch, cancellations) behind deterministic invariants before execution, and runs automated regression evaluations.
2. **Real-Time Voice & Sub-500ms Latency:**
   - Voice time-to-first-token (TTFT) was driven down from >1s to **~500ms**, with live caller interruption handling, streaming STT/TTS pipelines, and telephony failover.
3. **100% Production Reliability Mindset:**
   - Essential services happen in emergencies (e.g., furnace out at 2am). Netic's engineering blog emphasizes: *"95% reliability is nowhere near enough"* and *"We don't just fix bugs. When a customer cites an issue or we find one ourselves, we dig into the root cause."*

---

## 3. Active Engineering Roles on Netic's Ashby Board ($145K–$330K)

| Role | Location | Core Stack & Focus |
|------|----------|--------------------|
| **Software Engineer, Product** | SF / NYC (On-site) | React, TypeScript, Next.js (App Router/RSC), Python, Postgres, cloud infra, LLM APIs / RAG, end-to-end feature ownership (`jobs.ashbyhq.com/netic/2ae2cae2-03cb-4bc7-986a-a93de10f46df`) |
| **Software Engineer, Infrastructure** | SF / NYC (On-site) | GCP/AWS, Terraform, GitHub Actions, Kubernetes autoscaling, Postgres / pgBouncer, Datadog, IAM & network segmentation, spike handling (`jobs.ashbyhq.com/netic/178a50d3-f3e8-4031-829f-ce6d6f3ed245`) |
| **Forward Deployed Engineer** | SF (On-site) | Python (`asyncio`, FastAPI), TypeScript (Node, React), LLM/TTS/speech APIs, RAG, evals, high-concurrency customer debugging & SLAs |
| **Applied AI Engineer** | SF / NYC (On-site) | PyTorch/JAX, open-weight model serving, streaming inference, retrieval/agentic harnesses, A/B experimentation & evals |
| **Software Engineer, Sales Systems** | SF (On-site) | Python/TS, SQL, CRM/billing/warehouse syncs, idempotent event-driven pipelines, workflow orchestration |

**Netic Core Values:**
1. Obsess over the customer
2. Every second counts
3. Sweat the details
4. There are no blockers
5. Be self-directed
6. Seek and speak the truth
7. Enjoy the ride

---

## 4. Spotlight on Your Interviewer: Ze Huang

- **Current:** Engineering at Netic (joined July 2026, Bay Area). Tagline: *"Thinking about how to build intelligent systems at scale in the AI age."*
- **Career Arc (10+ years in Silicon Valley):**
  - **VP of Engineering @ Poseidon** (2025–2026) — Decentralized AI data processing and verifiable AI workloads.
  - **Founding Engineer & Team Lead @ Story Protocol** (2022–2025) — Built 0→1 core infrastructure, APIs, SDKs, and high-spike traffic systems.
  - **Founding Engineer @ DimeFi** (2021–2022) — Product & distributed systems engineering.
  - **Senior Software Engineer @ Uber** (2018–2021) — Fraud/gaming detection, stream & batch data pipelines, distributed microservices, ML systems.
  - **Design Verification Engineer @ Marvell Semiconductor** (2013–2018) — C++ simulation and hardware verification.
  - **Education:** University of Florida + ML specialization.
- **Technical Fluency:** Go, Python, C++, TypeScript/Node.js/React, SQL, MongoDB, Linux, distributed systems.
- **What Ze Evaluates:** Coming from hardware verification + Uber distributed systems + 0→1 startup leadership, Ze cares about **scientific debugging**:
  1. Reproducing the failure deterministically before guessing.
  2. Isolating the exact broken invariant (not papering over symptoms).
  3. Reasoning about concurrency, retries, partial failures, and boundary conditions.
  4. Using AI tools with high judgment (verifying hypotheses rather than pasting unverified patches).
  5. Clear, continuous verbal narration.

---

## 5. Broader Engineering Team Snapshot (LinkedIn)

| Cluster | Notable Engineers & Backgrounds | Likely Technical Signals |
|---------|---------------------------------|--------------------------|
| **Infra & Systems Leadership** | Greg Solovyev (Head of Infra, ex-Airtable/Airbyte/Cloudera), Ze Huang (ex-Uber/Story), Jake Laney (ex-Staff Payments @ Rippling), VoIP/Telephony engineers (ex-Flowroute) | Connection pooling, transaction/locking safety, idempotent retries, observability (Datadog), graceful degradation |
| **Voice & Agent Platform** | Zi Gao (ex-Databricks Spark), Ajay Arora (MIT — single-LLM voice harness), Isaac Na (ex-Addepar/Brex — Agent Platform), Daniel Fleming (MIT — custom LLM inference), Xinyi Chen (MIT — real-time voice) | Async task cancellation/races, streaming latency, state/context isolation across concurrent calls, deterministic action gating |
| **Product & Forward Deployed** | Theodore Klausner (Cornell), Jessica Zhu (ex-Scale AI GenAI Tech Lead), Will Furlow (Stanford), Charles Ide (ex-Scale AI), Sameer Das, Albert Yue (ex-Uber/DRW), Michael Zhao, Kyle Orciuch, Pau Kung | API contract mismatches, third-party CRM webhook quirks, timezone/scheduling edge cases, end-to-end ownership |

---

## 6. Predicted Bug Archetypes for a 45-Minute Debugging Round

Rather than a LeetCode graph/DP puzzle, expect a realistic service or multi-component bug in one of these categories:
1. **Async / Concurrency Race Conditions:** Double-booking check-then-act gaps, caller interruption task leaks, or cross-request context bleed.
2. **Idempotency & Distributed Retries:** Duplicate CRM/webhook writes on timeout retries, partial state mutations before an exception.
3. **Agent Execution Harness & Guardrails:** Malformed/retried LLM tool calls bypassing validation or firing irreversible actions.
4. **Database, Caching & Latency:** Stale cache after writes, N+1 queries, connection leaks on error paths, missing per-step latency instrumentation.
5. **Scheduling, State & API Contracts:** Timezone/boundary off-by-one bugs, missing state-machine branches, or frontend/backend payload mismatches.
