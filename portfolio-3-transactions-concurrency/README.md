# Portfolio 3 — Transactions and concurrency (7 marks)

Run python run_all.py from the root. Implemented examples are in the transaction section of run_all.py; checkout.sql is the successful illustrative workflow. Inspect transaction-tests.json for eight executed checks.

## Schedule and results
1. Rollback: set stock from 1 to 0 inside BEGIN IMMEDIATE; rollback restores 1.
2. Uncommitted read: connection A holds an uncommitted stock=0; separate B reads committed stock=1. No shared-cache/read_uncommitted exception is enabled.
3. Writer contention: A holds BEGIN IMMEDIATE; B attempts BEGIN IMMEDIATE, waits up to its 150 ms timeout and receives database-is-locked. A rolls back. This is lock contention, NOT a deadlock demonstration.
4. Snapshot: A begins a read transaction and reads 1; B changes stock to 2 and commits; A still reads 1, then commits its read transaction; the next A read sees 2.
5. Successful checkout: BEGIN IMMEDIATE serialises writers; conditional decrement requires stock>=1. The fixture ensures stock=1 and executes the successful SQL branch, adding order 100001, one item and one captured payment. Commit makes the set permanent to subsequent reads.
6. Second buyer: conditional decrement affects zero rows because stock=0. Test rolls back and asserts no decrement occurred. Production code must stop here and not insert an order.
7. Failure atomicity: after changing another product's stock, an intentional duplicate-customer violation triggers an explicit rollback. Stock returns to its initial value. Do not assume SQLite automatically rolls back the entire transaction on every statement error.

## ACID interpretation
Atomicity: successful multi-statement checkout commits together; explicit rollback undoes intermediate writes. Consistency: constraints and conditional update maintain the tested invariants. Isolation: independent connections show hidden uncommitted changes, one-writer locking and WAL snapshot reads. Durability: COMMIT records committed changes, but no power-failure test is claimed. Reopening the document store is a separate persistence check, not proof of crash durability for SQL.

## Concurrency choice
A naive read-stock then overwrite-stock sequence can lose business updates; this lab prevents overselling with a conditional update inside an explicit write transaction rather than demonstrating a fabricated lost-update trace. SQLite permits only one writer at a time; WAL permits concurrent readers and a writer. A production service should handle busy errors with bounded retry/backoff and an idempotency key, without charging a payment provider twice.

No actual payment gateway is contacted. External payment capture cannot be atomically committed by a local SQL transaction; use idempotent provider calls plus outbox/saga/reconciliation patterns in an extended design. No distributed payment atomicity is claimed here.
