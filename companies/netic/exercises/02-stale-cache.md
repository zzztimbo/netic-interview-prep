# Exercise 2: Stale CRM Customer Cache (Easy–Medium)

## Scenario
Before booking a job, Netic's agent checks the homeowner's service history from an external CRM. To meet latency targets, reads are cached in memory for 5 minutes. After an operator updates a customer's address or VIP flag, follow-up calls within 5 minutes still read the old address.

## Candidate Code
```python
import time

_cache = {}
CACHE_TTL = 300  # seconds


def get_customer_history(customer_id, fetch_from_crm):
    now = time.time()

    if customer_id in _cache:
        cached_data, cached_at = _cache[customer_id]
        if now - cached_at < CACHE_TTL:
            return cached_data

    data = fetch_from_crm(customer_id)
    _cache[customer_id] = (data, now)
    return data


def update_customer(customer_id, new_data, crm_update):
    crm_update(customer_id, new_data)
```

## Your Task (20 min)
1. Reproduce the stale-read sequence in a 5-line test.
2. Identify both the immediate missing invalidation and the subtle mutation/concurrency hazards (e.g., callers mutating the returned dict in place, or concurrent read + write ordering).
3. Apply a clean fix and compare write-invalidate vs. write-through vs. versioned cache keys.
4. Answer Ze's follow-ups:
   - What happens if you clear the cache *before* `crm_update`, vs. *after* `crm_update` fails, vs. a concurrent reader repopulating stale data during `crm_update`?
   - How does this change when 10 API replicas run behind a load balancer?

<details>
<summary>Root Cause & Reference Fix (Open After Attempting)</summary>

- **Root cause:** `update_customer` writes to the CRM without invalidating `_cache.pop(customer_id, None)` (after the CRM write succeeds). In addition, returning raw dict references from `_cache` lets callers accidentally mutate cached state.
- **Production hardening:** Shared Redis cache invalidated on write/CDC event, short TTL + version stamp, and `time.monotonic()` for local TTL math so wall-clock adjustments don't corrupt expiry.
</details>
