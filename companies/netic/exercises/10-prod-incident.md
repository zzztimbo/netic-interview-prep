# Exercise 10: 5:00 AM On-Call Production Incident (Hard)

## Scenario
It's **5:00 AM**. You get paged: a $50K/day HVAC enterprise customer's AI voice line is dropping incoming calls immediately after pickup.

### Incident Facts
- No code or config deploys in the last 24 hours.
- Newly onboarded customers work fine; this long-standing enterprise customer (and two others onboarded >3 months ago) started failing at **04:47 AM UTC**.
- Cron logs show `cleanup_old_data.py` ran at **04:45 AM UTC**.
- Application error logs show: `IndexError: list index out of range in initialize_conversation`.

## Candidate Code
```python
# cleanup_old_data.py — runs daily at 04:45 UTC
def cleanup_old_data(db, now_utc):
    cutoff = now_utc - timedelta(days=90)
    db.execute("DELETE FROM customer_Profiles_cache WHERE created_at < %s", [cutoff])
    db.execute("DELETE FROM call_sessions WHERE updated_at < %s", [cutoff])
```

```python
# voice_gateway.py — runs on every inbound call
def initialize_conversation(db, business_id: str, caller_phone: str):
    # db.query ALWAYS returns list[dict] (empty list [] when 0 rows match)
    tenant_cfg = db.query(
        "SELECT * FROM customer_profiles_cache WHERE business_id = %s",
        [business_id],
    )
    if tenant_cfg is None:
        tenant_cfg = [hydrate_tenant_profile(db, business_id)]

    recent_sessions = db.query(
        "SELECT * FROM call_sessions WHERE caller_phone = %s ORDER BY updated_at DESC LIMIT 1",
        [caller_phone],
    )
    prior_session = recent_sessions[0] if recent_sessions is not None else None

    return ConversationContext(profile=tenant_cfg[0], prior_session=prior_session)
```

## Your Task (25 min)
1. Connect the 04:45 AM cron job to the 04:47 AM `IndexError` for >90-day tenants, and list **every** bug across both files.
2. Separate **5:05 AM immediate mitigation** (how to restore live calls in <5 minutes) from the **permanent code & schema fix**.
3. Outline the post-mortem action items (monitoring, dry-run/TTL design, integration tests).

<details>
<summary>Root Cause & Reference Fix (Open After Attempting)</summary>

- **Root causes:**
  1. **`[] is not None` in Python:** `db.query(...)` returns `[]` when zero rows match, never `None`. Both `if tenant_cfg is None:` and `recent_sessions[0] if recent_sessions is not None` treat `[]` as present and crash with `IndexError: list index out of range` on `[0]`!
  2. **Destructive cron deleting active tenant config by `created_at`:** `cleanup_old_data` deletes `customer_profiles_cache` rows where `created_at < 90 days` — wiping every tenant onboarded >90 days ago at 04:45 AM! (And even for brand-new callers with 0 `call_sessions`, `recent_sessions[0]` also crashes!)
- **Immediate mitigation (5 AM):** Re-hydrate `customer_profiles_cache` for affected >90d `business_id`s + pause the cron job, then ship hotfix checking `if not tenant_cfg:` and `recent_sessions[0] if recent_sessions else None`.
</details>
