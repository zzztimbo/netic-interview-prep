"""Acceptance check suite shared by `run_drill.py` and `test_drills_suite.py`."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from types import ModuleType


def check_drill_01(mod: ModuleType) -> list[str]:
    failures: list[str] = []
    utc = timezone.utc
    s1 = datetime(2026, 12, 2, 10, 0, tzinfo=utc)
    s2 = datetime(2026, 12, 2, 14, 0, tzinfo=utc)

    # 1. Single-element and last-element slot lookup
    if mod.find_earliest_slot([s1], s1) != s1:
        failures.append("single-slot list failed to match exact preferred_time")
    if mod.find_earliest_slot([s1, s2], s2) != s2:
        failures.append("final slot of the day returned None instead of matching")
    if mod.find_earliest_slot([], s1) is not None:
        failures.append("empty slot list should return None")

    # 2. Unsorted slot list resilience
    if mod.find_earliest_slot([s2, s1], s1) != s1:
        failures.append("unsorted available_slots did not return the earliest qualifying slot")

    # 3. Naive datetime rejection
    try:
        mod.find_earliest_slot([s1], datetime(2026, 12, 2, 10, 0))
        failures.append("naive preferred_time did not raise ValueError")
    except ValueError:
        pass
    except Exception as exc:
        failures.append(f"naive preferred_time raised {type(exc).__name__} instead of ValueError")

    # 4. Mutable default / caller list isolation in build_reservation
    r_urgent = mod.build_reservation("cust_a", s1, is_emergency=True)
    r_normal = mod.build_reservation("cust_b", s2, is_emergency=False)
    if "emergency" in r_normal["tags"]:
        failures.append("emergency tag leaked from prior reservation into subsequent standard reservation")

    caller_tags = ["vip"]
    _ = mod.build_reservation("cust_c", s1, is_emergency=True, tags=caller_tags)
    if caller_tags != ["vip"]:
        failures.append("build_reservation mutated caller-supplied tags list in place")

    return failures


def check_drill_02(mod: ModuleType) -> list[str]:
    failures: list[str] = []

    async def _scenario_context_isolation() -> None:
        coord = mod.VoiceBookingCoordinator({"slot_10am", "slot_11am"})

        async def noop_crm(_cust: str, _slot: str) -> None:
            await asyncio.sleep(0.01)

        async def call_a() -> dict:
            coord.begin_call("call_A", "cust_A", "+14155550101")
            return await coord.process_booking_turn("call_A", "slot_10am", noop_crm)

        async def call_b() -> dict:
            await asyncio.sleep(0.002)
            coord.begin_call("call_B", "cust_B", "+14155550102")
            return await coord.process_booking_turn("call_B", "slot_11am", noop_crm)

        res_a, res_b = await asyncio.gather(call_a(), call_b())
        if res_a["customer_id"] != "cust_A" or res_a["phone"] != "+14155550101":
            failures.append(
                f"Call A context bled into another customer: got customer_id={res_a['customer_id']!r}"
            )
        if res_b["customer_id"] != "cust_B":
            failures.append(
                f"Call B context corrupted: got customer_id={res_b['customer_id']!r}"
            )

    async def _scenario_single_winner_and_rollback() -> None:
        coord = mod.VoiceBookingCoordinator({"slot_last"})

        async def noop_crm(_cust: str, _slot: str) -> None:
            await asyncio.sleep(0.005)

        coord.begin_call("c1", "cust_1", "+1001")
        coord.begin_call("c2", "cust_2", "+1002")

        r1, r2 = await asyncio.gather(
            coord.process_booking_turn("c1", "slot_last", noop_crm),
            coord.process_booking_turn("c2", "slot_last", noop_crm),
        )
        winners = [r for r in (r1, r2) if r["booked"]]
        if len(winners) != 1:
            failures.append(f"concurrent booking for same slot produced {len(winners)} winners (expected 1)")

        # Rollback check when crm_notify raises
        coord_fail = mod.VoiceBookingCoordinator({"slot_err"})
        coord_fail.begin_call("c_err", "cust_err", "+1999")

        async def failing_crm(_cust: str, _slot: str) -> None:
            raise RuntimeError("CRM 503 timeout")

        try:
            await coord_fail.process_booking_turn("c_err", "slot_err", failing_crm)
        except RuntimeError:
            pass
        if not coord_fail.is_slot_open("slot_err"):
            failures.append("slot remained unavailable after crm_notify raised an exception")

    try:
        asyncio.run(_scenario_context_isolation())
        asyncio.run(_scenario_single_winner_and_rollback())
    except Exception as exc:
        failures.append(f"unexpected exception during Drill 2 checks: {type(exc).__name__}: {exc}")

    return failures


def check_drill_03(mod: ModuleType) -> list[str]:
    failures: list[str] = []

    async def _run() -> None:
        worker = mod.WebhookBookingWorker()
        dispatch_calls = 0

        async def flaky_then_ok(payload: dict) -> str:
            nonlocal dispatch_calls
            dispatch_calls += 1
            await asyncio.sleep(0.01)
            if dispatch_calls == 1:
                raise ConnectionError("transient ServiceTitan timeout")
            return f"job_{payload['customer_id']}"

        payload = {"customer_id": "cust_42", "service": "HVAC"}

        # 1. Transient failure on attempt 1 must NOT poison subsequent retry
        try:
            await worker.handle_event("evt_1", payload, flaky_then_ok)
        except ConnectionError:
            pass

        retry_res = await worker.handle_event("evt_1", payload, flaky_then_ok)
        if retry_res.get("job_id") != "job_cust_42":
            failures.append(
                f"retry after transient dispatch error failed to dispatch: got {retry_res!r}"
            )

        # 2. Concurrent duplicate deliveries must dispatch exactly once
        worker2 = mod.WebhookBookingWorker()
        concurrent_dispatches = 0

        async def slow_dispatch(p: dict) -> str:
            nonlocal concurrent_dispatches
            concurrent_dispatches += 1
            await asyncio.sleep(0.02)
            return f"job_{p['customer_id']}"

        res_a, res_b = await asyncio.gather(
            worker2.handle_event("evt_dup", payload, slow_dispatch),
            worker2.handle_event("evt_dup", payload, slow_dispatch),
        )
        if concurrent_dispatches != 1:
            failures.append(
                f"concurrent duplicate webhook dispatched {concurrent_dispatches} jobs (expected 1)"
            )
        if res_a.get("job_id") != "job_cust_42" or res_b.get("job_id") != "job_cust_42":
            failures.append("concurrent duplicate callers did not receive consistent job_id result")

        # 3. Reusing same event_id with mutated payload must raise ValueError
        try:
            await worker2.handle_event(
                "evt_dup",
                {"customer_id": "cust_DIFFERENT", "service": "PLUMBING"},
                slow_dispatch,
            )
            failures.append("reusing event_id with conflicting payload did not raise ValueError")
        except ValueError:
            pass

    try:
        asyncio.run(_run())
    except Exception as exc:
        failures.append(f"unexpected exception during Drill 3 checks: {type(exc).__name__}: {exc}")

    return failures


def check_drill_04(mod: ModuleType) -> list[str]:
    failures: list[str] = []

    async def _run() -> None:
        booked_calls: list[tuple[str, str]] = []

        async def fake_book(cust_id: str, slot_id: str) -> bool:
            booked_calls.append((cust_id, slot_id))
            return slot_id == "slot_valid"

        # 1. Markdown-fenced JSON should parse cleanly without raising
        fenced = '```json\n{"action": "BOOK", "slot_id": "slot_valid", "spoken_reply": "Booked for 2pm!"}\n```'
        try:
            res_fenced = await mod.execute_agent_turn(
                fenced, "cust_1", ["slot_valid"], fake_book
            )
            if not isinstance(res_fenced, dict) or not res_fenced.get("booked"):
                failures.append("markdown-fenced valid BOOK response did not succeed")
        except Exception as exc:
            failures.append(f"markdown-fenced JSON crashed with {type(exc).__name__}")

        # 2. Malformed non-JSON output should return graceful clarification fallback
        try:
            res_bad = await mod.execute_agent_turn(
                "Sorry, thinking out loud: {broken json",
                "cust_1",
                ["slot_valid"],
                fake_book,
            )
            if not isinstance(res_bad, dict) or res_bad.get("booked") is not False:
                failures.append("malformed LLM output did not return safe non-booked fallback dict")
        except Exception as exc:
            failures.append(f"malformed LLM output crashed with {type(exc).__name__}")

        # 3. Hallucinated slot_id NOT in open_slots must be gated BEFORE calling book_slot_fn
        booked_calls.clear()
        hallucinated = '{"action": "BOOK", "slot_id": "slot_invented_3pm", "spoken_reply": "You are set for 3pm!"}'
        res_halluc = await mod.execute_agent_turn(
            hallucinated, "cust_1", ["slot_valid"], fake_book
        )
        if booked_calls:
            failures.append("action gate failed: book_slot_fn was invoked with hallucinated slot_id")
        if not isinstance(res_halluc, dict) or res_halluc.get("booked") is not False:
            failures.append("hallucinated slot_id returned booked=True instead of safe rejection")

        # 4. ASK_CLARIFICATION must return spoken reply dict instead of None
        clarify = '{"action": "ASK_CLARIFICATION", "slot_id": null, "spoken_reply": "Which morning works best?"}'
        res_clarify = await mod.execute_agent_turn(
            clarify, "cust_1", ["slot_valid"], fake_book
        )
        if not isinstance(res_clarify, dict) or res_clarify.get("spoken_reply") != "Which morning works best?":
            failures.append(f"ASK_CLARIFICATION returned {res_clarify!r} instead of spoken reply dict")

        # 5. Concurrent conflict (book_slot_fn returns False) must NOT claim booked=True
        conflict = '{"action": "BOOK", "slot_id": "slot_taken_just_now", "spoken_reply": "Booked!"}'
        res_conflict = await mod.execute_agent_turn(
            conflict,
            "cust_1",
            ["slot_taken_just_now"],
            fake_book,  # returns False because slot_id != "slot_valid"
        )
        if not isinstance(res_conflict, dict) or res_conflict.get("booked") is not False:
            failures.append("book_slot_fn returning False still reported booked=True to caller")

    try:
        asyncio.run(_run())
    except Exception as exc:
        failures.append(f"unexpected exception during Drill 4 checks: {type(exc).__name__}: {exc}")

    return failures


DRILL_REGISTRY = {
    1: ("drill_01_slot_scheduler", check_drill_01),
    2: ("drill_02_async_session_race", check_drill_02),
    3: ("drill_03_webhook_idempotency", check_drill_03),
    4: ("drill_04_action_gate_harness", check_drill_04),
}
