# Exercise 4: API Envelope Contract Mismatch (Medium)

## Scenario
Netic's operator dashboard (React/TypeScript) queries a FastAPI endpoint for open technician slots. `curl` confirms the backend returns open slots with HTTP 200, yet the UI renders "No slots available" with zero console errors.

## Candidate Code

### Backend (Python / FastAPI)
```python
@app.get("/slots")
def get_slots(date: str):
    slots = db.query_slots(date)
    # Example db result: [{"time": "10:00", "available": True}]
    return {"slots": slots, "date": date}
```

### Frontend (TypeScript)
```typescript
interface Slot {
  time: string;
  available: boolean;
}

async function fetchSlots(date: string): Promise<Slot[]> {
  const response = await fetch(`/slots?date=${encodeURIComponent(date)}`);
  const data = await response.json();
  return data;
}

// UI rendering logic:
const slots = await fetchSlots("2026-12-15");
if (!slots.length) {
  renderEmptyState("No slots available");
}
```

## Your Task (20 min)
1. Explain why `fetchSlots` compiles cleanly in TypeScript yet evaluates `!slots.length` as truthy at runtime without throwing.
2. Fix the contract cleanly and handle non-2xx HTTP responses (`!response.ok`).
3. Propose how to make this class of bug impossible across Python + TypeScript repositories.

<details>
<summary>Root Cause & Reference Fix (Open After Attempting)</summary>

- **Root cause:** `response.json()` returns `Promise<any>`, bypassing TypeScript's `Promise<Slot[]>` return type check. At runtime `data` is `{ slots: [...], date: "..." }`, so `data.length` is `undefined`, and `!undefined` is `true` — silently triggering the empty state!
- **Fix & prevention:** Check `if (!response.ok) throw ...`, parse `{ slots }: { slots: Slot[] }` (or validate with Zod), and generate typed TS clients directly from FastAPI's OpenAPI schema (`openapi-typescript`).
</details>
