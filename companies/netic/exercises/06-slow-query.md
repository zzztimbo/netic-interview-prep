# Exercise 6: Dashboard N+1 Query & Unbounded Scan (Medium)

## Scenario
Netic's business portal displays the 50 most recent jobs for a franchise. Small tenants (100 jobs) load in 180ms; enterprise franchises (25,000 jobs) time out after 30s and spike Postgres CPU.

## Candidate Code
```python
@app.get("/jobs")
def list_jobs(business_id: str, limit: int = 50):
    jobs = db.query(
        "SELECT * FROM jobs WHERE business_id = %s",
        (business_id,),
    )

    enriched = []
    for job in jobs:
        customer = db.query(
            "SELECT name, phone FROM customers WHERE id = %s",
            (job["customer_id"],),
        )[0]
        enriched.append({**job, "customer_name": customer["name"]})

    return enriched[:limit]
```

## Your Task (20 min)
1. Count how many SQL queries and rows execute for a tenant with 25,000 jobs when `limit=50` — and spot the hidden crash bug if a customer record is missing.
2. Rewrite the query + Python code to execute in **1 bounded query** with proper ordering and pagination.
3. Specify the exact composite index needed on `jobs` and explain why column order matters.

<details>
<summary>Root Cause & Reference Fix (Open After Attempting)</summary>

- **Root causes:**
  1. **Unbounded table scan before Python slicing:** Fetches all 25,000 `jobs` rows without `ORDER BY` or SQL `LIMIT`, then slices `[:limit]` at the very end!
  2. **N+1 query storm:** Runs 25,000 sequential `SELECT ... FROM customers` queries (even for the 24,950 rows discarded by `[:limit]`).
  3. **Crash + unbounded input hazards:** `[0]` raises `IndexError` if an orphaned `customer_id` exists (`LEFT JOIN` fixes this), and caller-supplied `limit` isn't capped (`min(max(limit, 1), 200)`).
- **Fix & Index:** Single `SELECT j.id, ..., c.name AS customer_name FROM jobs j LEFT JOIN customers c ON c.id = j.customer_id WHERE j.business_id = %s ORDER BY j.created_at DESC LIMIT %s` backed by `CREATE INDEX idx_jobs_business_created ON jobs (business_id, created_at DESC)`.
</details>
