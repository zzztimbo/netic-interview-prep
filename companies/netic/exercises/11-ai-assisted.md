# Exercise 11: AI-Assisted Specification & Edge-Case Audit (Medium–Hard)

## Scenario
During the interview AI tools are allowed. This exercise trains using AI **with rigor** against a concrete product specification:

### Business Pricing Specification
- Base dispatch fees: `HVAC = $50.00`, `PLUMBING = $75.00`, `ELECTRICAL = $60.00`, `PEST = $40.00` (case-insensitive input allowed, e.g. `"hvac"`).
- Emergency multiplier: `2.5x` base fee for `"basic"` and `"premium"` tiers, **capped at `1.5x`** for `"enterprise"` contract customers.
- Tier discounts (applied after emergency multiplier):
  - `"basic"`: `0%` discount
  - `"premium"`: `20%` discount
  - `"enterprise"`: `25%` discount
- Unknown `service_type` or `customer_tier` must raise `ValueError` (never silently default).
- Output must be exact two-decimal `float` or integer cents without IEEE-754 float drift (e.g., `56.25`, never `60.00000000000001`).

## Candidate Code
```python
def calculate_booking_fee(service_type: str, is_emergency: bool, customer_tier: str) -> float:
    base_fees = {
        "HVAC": 50,
        "PLUMBING": 75,
        "ELECTRICAL": 60,
        "PEST": 40,
    }

    fee = base_fees[service_type]

    if is_emergency:
        fee *= 2.5

    if customer_tier == "premium":
        fee *= 0.8
    elif customer_tier == "basic":
        fee *= 1.0

    return fee
```

## Your Task (20 min)
1. Enumerate every discrepancy between the implementation and the spec *before* asking AI to write code.
2. Use AI to generate a table-driven parametrized test suite covering every tier × emergency combination, case sensitivity, invalid inputs, and floating-point precision (`ELECTRICAL` + emergency + `premium` -> `60 * 2.5 * 0.8` vs float drift cases).
3. Implement a clean `Decimal` (or integer-cents) fix and verify every test passes.

<details>
<summary>Root Cause & Reference Fix (Open After Attempting)</summary>

- **Discrepancies found:**
  1. `"enterprise"` tier missing both its `1.5x` emergency cap (got `2.5x`) and its `25%` discount (got `0%`).
  2. Lowercase `"hvac"` raises `KeyError` instead of normalizing `.strip().upper()` and raising `ValueError` on unknown service types.
  3. Unknown `customer_tier` (e.g. `"vip"` typo) silently charges full price instead of raising `ValueError`.
  4. Binary floating-point math (`60 * 2.5 * 0.8` or `75 * 1.5 * 0.75`) risks float representation drift — compute in `Decimal` with `ROUND_HALF_UP` (or integer cents).
</details>
