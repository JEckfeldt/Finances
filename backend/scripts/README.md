# Backend scripts

Utilities that are **not** part of the running API. Safe to run manually for local development and benchmarking.

## Benchmark data generator

`benchmark_seed.py` creates a dedicated performance-test account with realistic finance data:

| Item | Value |
|------|--------|
| User | `benchmark@local.dev` / `benchmark123456` |
| Transactions | 10,000 (mix of income ~12% and expense ~88%) |
| Categories | Groceries, Dining, Gas, Shopping, Entertainment, Utilities, Healthcare, Travel, Subscriptions, Salary, Freelance, Investment, Other |
| Budgets | 9 monthly limits aligned to expense categories |
| Date span | January 1, **four years ago** through **today** (deterministic RNG seed `42`) |

Data is inserted with batched commits for speed. Deleting the benchmark user removes all related transactions and budgets (`ON DELETE CASCADE`).

### Prerequisites

1. **PostgreSQL running** (Docker Compose from repo root):

   ```bash
   docker compose up -d postgres
   ```

2. **Python venv** with backend dependencies (from `backend/`):

   ```bash
   python -m venv .venv
   source .venv/bin/activate          # macOS/Linux
   # .venv\Scripts\Activate.ps1       # Windows
   pip install -r requirements.txt
   ```

3. **Database URL** pointing at Compose Postgres on the host:

   ```bash
   # Root .env (default from .env.example)
   DATABASE_URL=postgresql+psycopg://finance_user:finance_pass@localhost:5432/finance_app
   ```

   The script loads `.env` from the repo root and `backend/`. It does **not** start the FastAPI app or change application code.

4. **Schema must exist** — tables are created when you start the backend once in development, or run migrations manually. Easiest path:

   ```bash
   docker compose up -d postgres backend
   # wait for backend health, then stop if you only need Postgres
   ```

   In development (`APP_ENV=development`), the API enables **DEBUG** logging on the `app.performance` logger at startup, so each SQL statement appears as `SQL ...ms | ...` in backend logs during benchmarking.

### Seed benchmark data

From `backend/` with venv activated:

```bash
cd backend
python scripts/benchmark_seed.py seed
```

If the benchmark user already exists:

```bash
python scripts/benchmark_seed.py seed --replace
```

Expected output includes transaction batch progress and a summary (user id, counts, date range).

### Clean up benchmark data

Removes only the benchmark user; other app users are untouched.

```bash
cd backend
python scripts/benchmark_seed.py cleanup
```

This deletes `benchmark@local.dev` and cascades to all of that user’s transactions and budgets.

### Collecting performance baselines

1. Seed data (above).
2. Start backend with logs visible:

   ```bash
   docker compose up backend
   # or: uvicorn app.main:app --reload
   ```

3. Log in as `benchmark@local.dev` / `benchmark123456`, or use cookie auth with curl.
4. Watch `app.performance` logs for lines like:

   ```text
   HTTP GET /dashboard 200 42.35ms queries=9 db=8.12ms
   ```

5. Hit endpoints of interest: `GET /dashboard`, `GET /transactions`, `GET /budgets/progress`.

### Notes

- **Local only** — do not run against production RDS.
- **Not for pytest** — integration tests use a separate `finance_app_test` database.
- Re-running `seed` without `--replace` exits with an error to avoid duplicate users.
