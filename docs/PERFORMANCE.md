# Performance Engineering Log

This document records **measurable** backend and infrastructure performance work on Jake's Finance Tracker. Each entry includes benchmark context, before/after metrics, and verification approach so improvements can be reproduced and discussed in reviews or interviews.

**Related tooling (not documented in depth here):**

- Request and SQL timing: `backend/app/core/performance.py` (`app.performance` logger)
- Local benchmark dataset: `backend/scripts/benchmark_seed.py` (see `backend/scripts/README.md`)

---

## Dashboard Analytics Query Optimization

**Status:** Complete  
**Area:** `GET /dashboard` — `backend/app/services/dashboard.py`  
**Date recorded:** July 2026

### Context

The dashboard endpoint aggregates balance, monthly summary, recent transactions, budget overview, and multi-month chart trends. Under load, it was a primary source of database work because it repeated similar `SUM` and `GROUP BY` operations over the `transactions` table.

The endpoint was profiled using a custom backend performance monitoring layer that tracks:

- HTTP request latency (wall time per request)
- SQL query count (statements executed during the request)
- SQL execution time (sum of cursor timings for those statements)

Instrumentation is enabled in development via `RequestTimingMiddleware` and SQLAlchemy cursor listeners. Log lines follow this shape:

```text
INFO [app.performance] HTTP GET /dashboard 200 42.17ms queries=10 db=18.12ms
DEBUG [app.performance] SQL 1.23ms | SELECT ...
```

### Benchmark environment

| Item | Value |
|------|--------|
| Database | PostgreSQL 16 (Docker Compose) |
| Application | FastAPI backend container, `APP_ENV=development` |
| Dataset | Benchmark seed script: **10,000** transactions, **9** budgets, user `benchmark@local.dev` |
| Measurement | `app.performance` logs during repeated `GET /dashboard` after login |
| Scope | Single endpoint; no caching or index changes in this optimization |

Reproduce the dataset:

```bash
docker compose up -d postgres
cd backend && python scripts/benchmark_seed.py seed --replace
```

Reproduce measurements: log in as the benchmark user, call `GET /dashboard`, and inspect backend logs for `HTTP GET /dashboard` lines (see `backend/scripts/README.md`).

---

### Before optimization

**`GET /dashboard` baseline (representative run):**

| Metric | Value |
|--------|--------|
| SQL queries | **10** |
| Database execution time | **18.12 ms** |
| Total API latency | **42.17 ms** |

#### Issue

The dashboard service issued **multiple independent aggregation queries** against `transactions`, including:

1. All-time income (`SUM` where `type = income`)
2. All-time expense (`SUM` where `type = expense`)
3. Current calendar month income (`SUM` with date bounds)
4. Current calendar month expense (`SUM` with date bounds)
5. Monthly income trend (`date_trunc` + `GROUP BY` per month)
6. Monthly expense trend (separate query with the same grouping pattern)

Additional queries (recent transactions list, budget list, budget progress aggregation, and authenticated user lookup) contributed to the total **10** round trips per request.

This design caused:

- Redundant scans/aggregations over the same table within one HTTP request
- Extra latency from multiple database round trips
- Higher CPU and I/O on PostgreSQL as transaction volume grows (benchmark: 10K rows)

---

### Changes implemented

Dashboard SQL was refactored in `backend/app/services/dashboard.py` without changing the public API contract (`DashboardResponse` in `backend/app/schemas/dashboard.py`).

| Change | Detail |
|--------|--------|
| **Conditional aggregation** | Replaced four separate `SUM(amount)` queries (all-time + current-month income/expense) with **one** PostgreSQL query using `SUM(...) FILTER (WHERE ...)` semantics via SQLAlchemy aggregate `.filter()`. |
| **Combined trend query** | Replaced separate monthly income and monthly expense trend queries with **one** `date_trunc('month', ...)` grouped query that returns both income and expense totals per month. |
| **Behavior preservation** | Default dashboard path still exposes all-time balance, current-month `monthly_summary`, six-month trend windows, top budget overview, and five recent transactions — same JSON shape and field semantics. |
| **Date-filter path** | When `start_date` / `end_date` query params are used, period income and expense are computed in a **single** filtered aggregation query (unchanged response semantics). |
| **AI insights unchanged** | Legacy helpers `_sum_by_type` and `_totals_by_month_and_type` remain for `ai_insights_service.py`; only the dashboard code path was consolidated. |

#### Verification (tests)

Automated coverage in `backend/tests/test_dashboard.py`:

- **`test_dashboard_response_fields_unchanged`** — response top-level and nested keys unchanged
- **`test_dashboard_monthly_trends_reflect_transaction_totals`** — monthly spending and comparison trends match known fixtures across current and previous month
- **`test_dashboard_sql_query_count`** — regression guard: **6** SQL round trips per `GET /dashboard` in the test harness (auth + consolidated dashboard work)
- Existing tests retained for balance, monthly summary scope, recent transaction limit, and budget overview behavior

No caching layer or new indexes were added as part of this change.

---

### After optimization

**`GET /dashboard` results (same benchmark environment; warm repeated requests):**

| Metric | Value |
|--------|--------|
| SQL queries | **6** |
| Database execution time | **~7.8 ms** average (sample below) |
| Total API latency | **~15.1 ms** average (sample below) |

#### Measured request examples

```text
HTTP GET /dashboard 200 17.69ms queries=6 db=10.44ms
HTTP GET /dashboard 200 13.30ms queries=6 db=6.51ms
HTTP GET /dashboard 200 14.61ms queries=6 db=7.24ms
HTTP GET /dashboard 200 14.71ms queries=6 db=7.10ms
```

**Query breakdown after optimization (typical request):**

1. Authenticated user lookup (`get_current_user`)
2. Consolidated balance and monthly summary aggregates
3. Recent transactions (limited list)
4. Budget progress — budget rows
5. Budget progress — current-month expense aggregation by category
6. Combined monthly income/expense trend aggregation

---

### Improvement summary

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| SQL queries | 10 | 6 | **−4 (−40%)** |
| Database execution time | 18.12 ms | ~7.8 ms avg | **~−57%** |
| Total API latency | 42.17 ms | ~15.1 ms avg | **~−64%** |

*Percent improvements use the documented baseline vs. the average of the four sample runs above. Latency varies with hardware, container load, and cache state; always compare using the same environment and dataset.*

---

### Resume bullet candidate

> Instrumented backend API performance and optimized PostgreSQL dashboard analytics queries, reducing database round trips by 40%, query execution time by 57%, and API latency by 64% under a 10K transaction benchmark workload.

---

## Future entries (placeholder)

Document subsequent work here (e.g. transaction list pagination, AI insights query consolidation, Redis caching, composite indexes) using the same **Context → Before → Changes → After → Summary** structure.
