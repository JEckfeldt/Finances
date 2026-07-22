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

## Frontend CI/CD Build Optimization

**Status:** Complete  
**Area:** CD workflow — `.github/workflows/deploy.yml` (frontend image build/push only)  
**Date recorded:** July 2026

### Problem

- Frontend Docker image build and push during CD took approximately **3 minutes 6 seconds**.
- Every GitHub Actions deployment performed a **cold Docker build**.
- `npm` dependencies and Next.js build layers were rebuilt on every deployment because **Docker layer caching was not enabled**.

---

### Investigation

The deployment workflow was audited. Findings:

| Finding | Detail |
|---------|--------|
| Layer caching | **Not enabled** — deploy used plain `docker build` / `docker push` on ephemeral `ubuntu-latest` runners |
| Dockerfile | **Already well structured** — multi-stage `deps` → `builder` → `runner` with lockfile-before-`npm ci` ordering |
| Bottleneck | Repeated **`npm ci`** and **`next build`** on every deploy, not poor Dockerfile layout |

---

### Implementation

| Change | Detail |
|--------|--------|
| **Build action** | Replaced the raw frontend `docker build` / `docker push` step with **`docker/build-push-action@v6`** and **`docker/setup-buildx-action@v3`** |
| **BuildKit cache** | Enabled GitHub Actions cache export/import: `cache-from: type=gha`, `cache-to: type=gha,mode=max` |
| **Preserved behavior** | Same ECR image tag (`{repository}:{commit-sha}`), push to ECR, `NEXT_PUBLIC_API_URL` build argument, and runtime application behavior |
| **Dockerfile** | **No changes** — existing layer order continued to work with BuildKit cache |
| **Scope** | Frontend deploy step only; backend image build remains unchanged |
| **Permissions** | Added `actions: write` on the workflow token so the GHA cache backend can store BuildKit layers |

---

### Results

**Baseline (cold build, no GHA cache):**

| Step | Duration |
|------|----------|
| Frontend build & push | **~3 min 6 s** |

**After cache warm-up (unchanged frontend layers between deploys):**

| Step | Duration |
|------|----------|
| Frontend build & push | **~5 s** |

**Highlights:**

- Approximately **97% reduction** in frontend build/push time on warm cache hits.
- Docker layers (**`npm ci`**, builder context, **`next build`**, runner copies) are **reused across deployments** instead of rebuilding dependencies on every run.
- **Faster deployments** with **identical** application behavior and image tagging.

---

### Engineering notes

- The **first deployment** after enabling cache **populated** the BuildKit GHA cache (`mode=max` retains intermediate stage layers).
- **Subsequent deployments** with matching layers demonstrated the measured improvement (~5 s vs ~3 min 6 s).
- **Backend** image build (still uncached `docker build`) and **ECS service stability waits** for backend and frontend are now the **primary remaining** deployment time contributors.

---

### Resume bullet candidate

> Enabled Docker BuildKit GitHub Actions cache for frontend ECR builds, reducing warm CD build/push time from ~3 minutes to ~5 seconds (~97%) without changing the Dockerfile or application behavior.

---

## ECS Deployment Optimization Results

**Status:** Complete  
**Area:** AWS Application Load Balancer target groups (frontend + backend ECS services)  
**Date recorded:** July 2026

### Original bottleneck

GitHub Actions CD uses `aws-actions/amazon-ecs-deploy-task-definition` with **`wait-for-service-stability: true`** for each service. The **“Deploy backend to ECS”** and **“Deploy frontend to ECS”** steps were each taking about **3 minutes** — not because registering a new task definition is slow, but because ECS waits for a **Fargate rolling deployment** to finish:

| Factor | Role in wall time |
|--------|-------------------|
| **`wait-for-service-stability`** | Blocks the workflow until the primary deployment reaches steady state (desired count, healthy tasks behind the load balancer). |
| **ALB target group health checks** | A new task is not “done” until the target group marks it **healthy** (`HealthyThresholdCount` consecutive successes on `HealthCheckIntervalSeconds`). |
| **Fargate rolling behavior** | With **desiredCount = 1** and typical **minimumHealthyPercent = 100%**, ECS starts a replacement task, waits for LB health, then drains the old task. |

Image pull, container start, and **`healthCheckGracePeriodSeconds`** still contribute, but the audit showed **health-check convergence** as a large, tunable slice of the ~3 minute per-service deploy steps.

---

### Configuration changes made

Both **frontend** and **backend** ALB target groups were updated (ECS services unchanged; workflow unchanged):

| Setting | Before | After |
|---------|--------|-------|
| **Health check path** | `/health` | `/health` (unchanged) |
| **Health check interval** | 30 s | **10 s** |
| **Health check timeout** | 5 s | 5 s (unchanged) |
| **Healthy threshold** | 5 consecutive successes | **2 consecutive successes** |
| **Unhealthy threshold** | 2 consecutive failures | 2 (unchanged) |

---

### Before vs after timing

Measured on production CD (**Deploy … to ECS** step duration, approximate):

| Step | Before | After | Δ |
|------|--------|-------|---|
| Deploy backend to ECS | **~3 min** | **~2 min** | **~−1 min** |
| Deploy frontend to ECS | **~3 min** | **~2 min** | **~−1 min** |
| **Combined ECS stability wait** | **~6 min** | **~4 min** | **~−2 min** |

Other pipeline stages (image build/push, task definition render, post-deploy curl checks) were not changed as part of this optimization.

---

### Why the improvement happened

1. **Faster ALB health convergence** — Checks run every **10 s** instead of **30 s**, so the load balancer can observe successful responses more frequently.
2. **Fewer successes required** — **2** consecutive passes replace **5**, shortening the minimum time from first good check to **healthy** (roughly on the order of **(threshold − 1) × interval**, plus app startup and grace period).
3. **Shorter path to steady state** — ECS **`wait-for-service-stability`** completes once the new task is registered and **healthy** in the target group and the deployment reaches steady state; tightening TG settings reduced delay between **task registration** and **service stable** without changing application code or the deploy workflow.

Health checks still hit **`/health`** with a **5 s** timeout and **2** failed checks before **unhealthy**, preserving a reasonable failure-detection floor.

---

### Remaining optimization opportunities

| Opportunity | Rationale |
|-------------|-----------|
| **Parallel backend and frontend ECS deploys** | Services are independent; running both stability waits concurrently could save ~**2 min** wall-clock vs sequential deploys (after images are built). |
| **Reduce ECR image pull time** | Fargate **pullStartedAt → pullStoppedAt** still adds tens of seconds per new task; smaller images and warm nodes help. |
| **Backend Docker image optimization** | Backend build is still uncached in GHA; slimmer images improve pull and cold-start on the task side. |
| **Review target group deregistration delay** | Default **deregistration_delay** can lengthen drain tail on old targets; worth profiling if deploy steps still have a long tail after **healthy**. |
| **ECS desired count / deployment strategy** | **desiredCount**, **minimumHealthyPercent**, and **maximumPercent** trade deploy speed vs availability; document before changing production SLOs. |

---

### Resume bullet candidate

> Profiled ECS Fargate deploy latency (ALB health checks + `wait-for-service-stability`), tuned target group intervals and healthy thresholds for `/health`, and cut per-service ECS deploy wait by ~1 minute (~2 minutes total) without code or pipeline changes.

---

## Future entries (placeholder)

Document subsequent work here (e.g. transaction list pagination, AI insights query consolidation, Redis caching, composite indexes) using the same **Context → Before → Changes → After → Summary** structure.
