# Exercise 7: Lock-Ordering Deadlock Under Concurrent Load (Medium–Hard)

## Scenario
Netic's billing worker processes customer invoice captures concurrently with operator-initiated refunds. Under light traffic everything passes; during busy Monday mornings worker threads hang indefinitely with 0% CPU until killed.

## Candidate Code
```python
import threading

payment_ledger_lock = threading.Lock()
booking_ledger_lock = threading.Lock()


def process_payment(payment_id, booking_id, amount):
    payment_ledger_lock.acquire()
    booking_ledger_lock.acquire()
    try:
        record_payment(payment_id, booking_id, amount)
        mark_booking_paid(booking_id, payment_id)
    finally:
        booking_ledger_lock.release()
        payment_ledger_lock.release()


def process_refund(refund_id, booking_id, amount):
    booking_ledger_lock.acquire()
    payment_ledger_lock.acquire()
    try:
        mark_booking_refunded(booking_id, refund_id)
        record_refund(refund_id, booking_id, amount)
    finally:
        payment_ledger_lock.release()
        booking_ledger_lock.release()
```

## Your Task (20 min)
1. Trace the exact 2-thread interleaving that deadlocks forever — AND spot the secondary exception-safety bug if acquiring the *second* lock raises or gets interrupted before entering `try:`.
2. Fix both lock ordering and context-manager (`with`) safety.
3. Explain how this exact deadlock manifests inside Postgres transactions updating two tables (`payments` and `bookings`) in opposite order, and how to diagnose/prevent it in production.

<details>
<summary>Root Cause & Reference Fix (Open After Attempting)</summary>

- **Root causes:**
  1. **AB-BA lock cycle:** `process_payment` acquires `payment -> booking` while `process_refund` acquires `booking -> payment`.
  2. **Leak outside `try`:** Both `acquire()` calls sit *before* `try:`, so any error acquiring the second lock leaks the first lock permanently.
- **Fix:** Enforce a global canonical lock hierarchy (`with booking_ledger_lock, payment_ledger_lock:` in both functions), and in Postgres update parent/child rows in a consistent table + primary-key order within short transactions (never holding locks across external Stripe/CRM HTTP calls).
</details>
