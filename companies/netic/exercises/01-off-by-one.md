# Exercise 1: Slot Lookup Off-By-One (Easy)

## Scenario
Netic's booking service matches an incoming HVAC customer call to the earliest available appointment slot at or after the customer's requested time. Customers occasionally get told "No availability today" even when the final slot of the day is still open.

## Candidate Code
```python
def find_earliest_slot(available_slots, preferred_time):
    """
    Find the earliest available slot at or after preferred_time.
    available_slots: list of datetime objects, sorted ascending
    preferred_time: datetime object
    Returns: the earliest slot >= preferred_time, or None
    """
    for i in range(len(available_slots) - 1):
        if available_slots[i] >= preferred_time:
            return available_slots[i]
    return None
```

## Your Task (15 min)
1. State the expected invariant vs. observed failure mode.
2. Write the smallest test input(s) that trigger the bug (including a 1-element list and last-slot match).
3. Apply a minimal fix and verify boundary cases: empty list, single slot, exact match, all slots earlier than `preferred_time`.
4. Answer Ze's follow-ups:
   - What if `available_slots` is large or unsorted?
   - What happens if naive and timezone-aware `datetime` objects are mixed?

<details>
<summary>Root Cause & Reference Fix (Open After Attempting)</summary>

- **Root cause:** `range(len(available_slots) - 1)` skips the last element (`index == len - 1`), and returns `range(0, -1)` (empty) when `len(available_slots) == 1`.
- **Minimal fix:** Iterate directly (`for slot in available_slots:`) or use `bisect.bisect_left(available_slots, preferred_time)` for $O(\log n)$ lookup on sorted slots, validating timezone awareness first.
</details>
