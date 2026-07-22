# Performance Engineering Log

This document records **measurable** backend and infrastructure performance work on Jake's Finance Tracker. Each entry includes benchmark context, before/after metrics, and verification approach so improvements can be reproduced and discussed in reviews or interviews.

**Related tooling (not documented in depth here):**

- Request and SQL timing: `backend/app/core/performance.py` (`app.performance` logger)
- AI insights pipeline timing and cache logging: same module (`log_ai_insights_pipeline`)
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

## AI Insights Caching Optimization

**Status:** Complete  
**Area:** `POST /ai/insights` — `backend/app/services/ai_insights_service.py`, `backend/app/services/ai_insights_cache.py`  
**Date recorded:** July 2026

### Problem identified

Repeat `POST /ai/insights` requests on the benchmark account were dominated by Gemini latency, not database work.

| Symptom | Detail |
|---------|--------|
| User-visible delay | ~7 seconds per uncached insights request |
| Dataset | Benchmark seed: **10,001** transactions (same user as dashboard benchmark), user `benchmark@local.dev` |
| Database | Not the bottleneck |

**Baseline metrics (cache miss, representative Docker Compose run):**

| Metric | Value |
|--------|--------|
| `transactions_total` | **10,001** |
| `transactions_current_month` | 133 (same run) |
| Database fetch (context + metrics counts) | **~26.58 ms** (`fetch=` in insights log) |
| Prompt construction | **~0.02 ms** (negligible) |
| Gemini generation | **~7,409 ms** |
| Gemini input tokens | **681** |
| Gemini output tokens | **384** |
| Total request duration | **~7,479 ms** |

Example log line:

```text
INFO [app.performance] AI insights user_id=3 cache=miss fetch=26.58ms prompt_build=0.02ms transactions_total=10001 transactions_current_month=133 prompt_chars=1680 prompt_tokens_est=420 gemini=7409.39ms gemini_in_tokens=681 gemini_out_tokens=384 total=7479.27ms ai_enabled=True
INFO [app.performance] HTTP POST /ai/insights 200 7501.09ms queries=10 db=17.20ms
```

---

### Investigation

Before changing behavior, the insights pipeline was instrumented (`log_ai_insights_pipeline` in `backend/app/core/performance.py`) to measure each request:

| Signal | Purpose |
|--------|---------|
| Database fetch time | Time to load insight context (aggregates + metric counts) |
| Prompt construction time | Time to build the prompt string |
| Prompt size | Character count and estimated token count |
| Gemini latency | Wall time for `generate_content` |
| Token usage | Provider `usage_metadata` (input and output tokens) |
| Total request latency | End-to-end time in `generate_financial_insights` |
| Cache result | `cache=hit` or `cache=miss` (added with caching) |

Logs contain **no** raw financial payloads (amounts, categories, or prompt text).

Profiling conclusion: with ~681 input tokens and sub-30 ms database work, **repeated Gemini generation** on every dashboard refresh was the bottleneck.

---

### Changes implemented

| Change | Detail |
|--------|--------|
| **Fingerprint-based cache** | After building `FinancialInsightContext`, a **SHA-256** fingerprint is computed from insight-relevant aggregates (month label, current-month income/expense, spending by category, budget utilization, recent monthly trends). |
| **Per-user storage** | In-process cache (`ai_insights_cache.py`) stores the last successful `AIInsightsResponse` per `user_id` keyed by fingerprint. |
| **Invalidation** | Cache misses when financial state affecting the prompt changes: new/updated/deleted **transactions**, **budget** changes, or **calendar month rollover** (month label and trend window shift). |
| **Cache hit path** | Matching fingerprint returns the stored response **without** rebuilding the prompt or calling Gemini. |
| **Cache miss path** | Unchanged prompt and model behavior; successful responses are stored when `AI_ENABLED=true`. |
| **API contract** | `AIInsightsResponse` JSON shape unchanged. |
| **Tests** | `test_insights_cache_hit_returns_existing_insight`, `test_insights_cache_regenerates_when_financial_data_changes` in `backend/tests/test_ai.py`. |

Reproduce measurements: log in as the benchmark user, open the dashboard (or call `POST /ai/insights` twice without changing data), and inspect `AI insights` lines in backend logs.

---

### After optimization (cache hit)

**Same benchmark environment; second request with unchanged financial aggregates:**

| Metric | Value |
|--------|--------|
| Cache | **hit** |
| Database fetch | **~25.90 ms** |
| Prompt construction | **0 ms** (skipped) |
| Gemini generation | **skipped** |
| Gemini tokens | **0** (no API call) |
| Total request duration | **~26 ms** |

Example log lines:

```text
INFO [app.performance] AI insights user_id=3 cache=hit fetch=25.90ms prompt_build=0.00ms transactions_total=10001 transactions_current_month=133 prompt_chars=0 prompt_tokens_est=0 gemini=n/a gemini_in_tokens=n/a gemini_out_tokens=n/a total=26.02ms ai_enabled=True
INFO [app.performance] HTTP POST /ai/insights 200 30.02ms queries=10 db=18.43ms
```

---

### Improvement summary

| Metric | Before (cache miss) | After (cache hit) | Improvement |
|--------|---------------------|-------------------|-------------|
| Total API latency | ~7,479 ms | ~26 ms | **~−99.7%** on repeat requests |
| Gemini latency | ~7,409 ms | 0 ms (skipped) | **No duplicate inference** |
| Token usage | 681 in + 384 out | 0 | **Avoids repeat API cost** |

*First request after a data change remains a cache miss and still invokes Gemini. Latency varies with network and provider load; compare using the same environment and unchanged data between requests.*

---

### Architecture note

The cache is **in-process** (per backend worker). That fits the current **single-instance** Docker Compose and typical single-task deployment: repeat dashboard loads on the same process avoid redundant Gemini calls.

For **multi-instance** production (multiple ECS tasks or Uvicorn workers), each instance maintains its own cache. A shared store (e.g. **Redis**) keyed by `(user_id, fingerprint)` would be a natural follow-up to deduplicate insights across instances.

---

### Resume bullet candidate

> Profiled AI insights latency (681-token prompts, ~7.4s Gemini vs ~26ms DB), added SHA-256 fingerprint caching of insight responses, and reduced repeat `POST /ai/insights` latency by ~99.7% while eliminating duplicate Gemini token usage on unchanged financial data.

---

## Future entries (placeholder)

Document subsequent work here (e.g. transaction list pagination, AI insights query consolidation, Redis caching, composite indexes) using the same **Context → Before → Changes → After → Summary** structure.
