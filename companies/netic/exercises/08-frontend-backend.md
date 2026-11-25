# Exercise 8: Full-Stack Timezone & Cancellation Filter Desync (Medium)

## Scenario
Netic's homeowner portal shows upcoming appointments for a selected calendar date. West Coast customers report two bugs on the same screen:
1. A 6:00 PM Pacific appointment booked for Dec 15 disappears from Dec 15 and shows up under Dec 16 instead.
2. Cancelled appointments still appear as active cards in the list.

## Candidate Code

### Backend (Python / FastAPI)
```python
@app.get("/appointments")
def list_appointments(customer_id: str):
    # Stored in UTC in Postgres; e.g. 2026-12-15 18:00 PST == "2026-12-16T02:00:00Z"
    rows = db.query_appointments(customer_id)
    return [
        {
            "id": r["id"],
            "start_time": r["start_time_utc"].isoformat().replace("+00:00", "Z"),
            "service_type": r["service_type"],
            "is_cancelled": r["is_cancelled"],
        }
        for r in rows
    ]
```

### Frontend (TypeScript / React)
```typescript
interface AppointmentDTO {
  id: string;
  start_time: string;
  service_type: string;
  cancelled?: boolean;
}

export function getActiveAppointmentsForDate(
  appointments: AppointmentDTO[],
  selectedLocalDate: string, // "2026-12-15" in user's local timezone
): AppointmentDTO[] {
  return appointments.filter((appt) => {
    const apptDate = appt.start_time.slice(0, 10);
    return !appt.cancelled && apptDate === selectedLocalDate;
  });
}
```

## Your Task (20 min)
1. Trace an appointment at `2026-12-15 18:00 America/Los_Angeles` (`2026-12-16T02:00:00Z`) with `is_cancelled: True` from Postgres through FastAPI into `getActiveAppointmentsForDate`.
2. Pinpoint both independent bugs causing the two user-reported symptoms.
3. Fix the date-matching logic (accounting for the business/customer IANA timezone, e.g. `America/Los_Angeles`, rather than slicing raw UTC strings) and align the cancellation field contract.

<details>
<summary>Root Cause & Reference Fix (Open After Attempting)</summary>

- **Root causes:**
  1. **UTC string slicing (`appt.start_time.slice(0, 10)`):** `2026-12-16T02:00:00Z` slices to `"2026-12-16"` even though in `America/Los_Angeles` (UTC-8) it is `2026-12-15` at 6:00 PM! Format the instant in the service location's explicit IANA timezone (`Intl.DateTimeFormat("en-CA", { timeZone: serviceTimeZone }).format(new Date(appt.start_time))`).
  2. **Optional field typo (`cancelled?: boolean` vs `is_cancelled: bool`):** Because `cancelled` was typed optional, `appt.cancelled` is always `undefined`, so `!appt.cancelled` is always `true` — showing cancelled appointments forever.
</details>
