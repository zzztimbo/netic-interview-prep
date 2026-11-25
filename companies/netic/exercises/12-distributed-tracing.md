# Exercise 12: Voice Pipeline Latency & Observability Diagnosis (Hard)

## Scenario
Netic's real-time voice agent targets sub-500ms turn response latency. Enterprise customers report intermittent 9–12 second pauses before the agent speaks back. Currently, production logs only show:
`INFO Call turn completed in 11.42s`

## Candidate Code
```python
import asyncio
import time


async def handle_voice_turn(audio_chunk, session_id: str, stt, crm, booking_api, llm, tts, logger):
    start = time.perf_counter()

    transcript = await stt.transcribe(audio_chunk)
    customer = await crm.get_customer_by_session(session_id)
    open_slots = await booking_api.get_open_slots(customer.zip_code)

    decision = await llm.generate_turn(
        transcript=transcript,
        customer=customer,
        open_slots=open_slots,
    )

    if decision.action == "BOOK":
        await booking_api.create_booking(customer.id, decision.slot_id)

    audio_reply = await tts.synthesize(decision.spoken_text)

    elapsed_ms = (time.perf_counter() - start) * 1000
    logger.info("Call turn completed in %.2fms", elapsed_ms)
    return audio_reply
```

## Your Task (25 min)
1. Identify both the **observability blind spots** (why on-call can't bisect the 11.4s spike) and the **sequential execution bottlenecks** hiding inside `handle_voice_turn`.
2. Add structured per-span timing + error attribution (`trace_id` / `session_id` + stage durations even when a stage raises an exception or times out).
3. Optimize the pipeline latency without sacrificing correctness (parallelizing independent I/O, per-call timeouts, streaming LLM → TTS for sub-500ms TTFT).

<details>
<summary>Root Cause & Reference Fix (Open After Attempting)</summary>

- **Root causes & optimizations:**
  1. **Zero stage spans + lost telemetry on timeout/exception:** Wrap each stage in a lightweight async span helper recording `duration_ms` and `status` in a `finally:` block keyed by `session_id`/`turn_id`.
  2. **Unnecessary serial awaits:** `stt.transcribe(audio_chunk)` and `crm.get_customer_by_session(session_id)` have zero data dependency — run them concurrently with `asyncio.gather(...)` (and pre-warm/cache `customer` + `open_slots` when the call connects!).
  3. **No timeouts or streaming:** Enforce `asyncio.wait_for(..., timeout=...)` per upstream dependency with graceful spoken hold/failover ("One moment while I pull up the schedule"), and stream tokens from `llm` into `tts` chunk-by-chunk instead of awaiting full generation.
</details>
