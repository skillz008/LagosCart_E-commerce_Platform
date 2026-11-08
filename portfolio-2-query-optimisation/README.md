# Portfolio 2 — Query processing and optimisation (7 marks)

Six SQL tasks are implemented in queries.sql: customer history, monthly captured sales, top ordered products, customers with no orders, customer spending ranks using a CTE/window function, and low-stock alerts. CSVs contain actual results, not illustrative output. `all-query-plans.json` records all six plans after indexing.

## Controlled comparison
Benchmark Q1 uses customer_id=42 and date >=2026-04-01 over 100,000 orders. Python 3.12.8, SQLite 3.46.1; random seed 8103. Run three warmups then 31 fully fetched repetitions for each condition on the same connection. Compare medians with perf_counter_ns. Baseline has no secondary orders index (the integer PK remains). Intervention creates (customer_id, ordered_at DESC), a line-item product index and runs ANALYZE. Only the orders index directly affects Q1; statistics also change, so the intervention is indexing plus updated planner statistics, not a perfectly isolated single-variable experiment.

Original measured median: 3.210269 ms before; 0.028617 ms after; ratio 112.18x. Both return the same 34 rows. Before: SCAN orders and USE TEMP B-TREE FOR ORDER BY. After: SEARCH orders USING INDEX idx_orders_customer_date (customer_id=? AND ordered_at>?).

The equality on customer_id narrows the leading index key; the date range scans the relevant suffix in date order, avoiding a separate sorting structure. status is not covered, so the engine still fetches matching table rows. This is a selective lookup, not proof that all queries improve. Indexes also consume space and add write maintenance. Nonselective reporting queries may reasonably scan many rows.

## Limits and next experiments
These are warm-cache, single-process, sequential measurements. Before always runs first; no cache flush, concurrent load, network or cloud IO is represented. Millisecond values are environment-specific, especially the tiny indexed duration. No timings for Q2-Q6 or insert overhead are claimed. Repeat with alternating conditions, independent processes, larger data, multiple parameter values and write-heavy workloads before production recommendations.

See benchmark.json, timings.csv, performance.png and the six CSV result files. Baseline benchmark occurs before the separate checkout test adds order 100001.
