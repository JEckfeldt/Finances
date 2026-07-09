# Project Status

Living document tracking what has been built and what remains.

Last updated: July 9, 2026

---

## Vision

Personal finance management platform. Intended user flow:

1. User authenticates
2. Lands on a personalized financial dashboard
3. Views current financial information
4. Manages transactions and budgets
5. All data is isolated per authenticated user

Design direction: Clean, modern, calm, professional, minimal. Off-white backgrounds, soft green accents, neutral text, Geist Sans typography.

---

## Milestone Progress

| Milestone | Status | Summary |
|-----------|--------|---------|
| M1 — Project foundation | Complete | Monorepo scaffold, Next.js + FastAPI + Docker Postgres |
| M2 — Pages, transactions, DB | Complete | UI shell, themed pages, transaction CRUD (create/view), DB connected |
| M3 — Authentication (JWT) | Complete | Register/login, JWT auth, protected routes, password hashing |
| M4 — User isolation | Complete | Transactions scoped to authenticated user via JWT |
| M5 — Budget CRUD | Complete | Budget model, CRUD API, progress calculation, functional budgets page |
| M6 — Dashboard analytics | Complete | Live balance, monthly summary, budget progress, recent transactions, spending chart |
| M7 — Transaction management | Complete | Full transaction CRUD, filtering, category normalization, FK constraints |
| M8 — Dashboard and UX refinement | Complete | Income vs expense chart, pagination, loading/error states, `/auth/me` |
| M9 — Deployment and production readiness | Complete | Frontend Docker container, full-stack Compose, env docs, startup validation |
| M10 — Automated backend testing | Complete | pytest suite, isolated test database, auth/transaction/budget/dashboard coverage |

---

## What Is Implemented

### Infrastructure

- Monorepo layout (`frontend/`, `backend/`, root config)
- Docker Compose: PostgreSQL 16, FastAPI backend, Next.js frontend (all with health checks)
- Environment config (`.env.example`, `APP_ENV`, `CORS_ORIGINS`, `DATABASE_URL`, `SECRET_KEY`, `NEXT_PUBLIC_API_URL`, `TEST_DATABASE_URL`)
- Production startup skips automatic schema changes (`APP_ENV=production`)
- Startup validation for required config and database connectivity
- Structured logging on backend startup and shutdown

### Frontend

- Next.js 15 (App Router, TypeScript, Tailwind CSS v4)
- shadcn/ui, React Hook Form + Zod, Lucide React, Recharts
- Off-white / soft-green theme; Geist Sans via `next/font`
- Full-height sidebar app shell; authenticated routes behind `AuthGuard`
- Login and registration pages; JWT stored in `localStorage`
- Loading skeletons and error states with retry

#### Pages

| Route | Status | Details |
|-------|--------|---------|
| `/login` | Functional | Email/password form, stores JWT, redirects to dashboard |
| `/register` | Functional | Email/password registration (min 8 chars), redirects to login |
| `/dashboard` | Functional | All-time balance; current-month income/expenses; top 5 budgets by usage; 5 recent transactions; charts |
| `/transactions` | Functional | Create/edit/delete with user-selected date; free-text category; search, type/category filters, pagination |
| `/budgets` | Functional | Add/edit/delete budgets, progress bars, loading/error states |

### Backend

- FastAPI with CORS, SQLAlchemy 2.x, Pydantic schemas
- Health endpoint: `GET /health`
- Password hashing (passlib + bcrypt), JWT auth (`python-jose`)
- All data routes protected and scoped to authenticated user
- Category normalization (trim + title case); case-insensitive budget matching
- Lightweight startup migrations for legacy databases
- pytest suite with isolated `finance_app_test` database

#### Models

| Model | Fields |
|-------|--------|
| `User` | `id`, `email` (unique), `hashed_password`, `created_at` |
| `Transaction` | `id`, `user_id` (FK CASCADE), `description`, `amount`, `type`, `category`, `transaction_date`, `created_at` |
| `Budget` | `id`, `user_id` (FK CASCADE), `category`, `limit_amount`, `created_at`, `updated_at` |

#### API Endpoints

| Method | Endpoint | Notes |
|--------|----------|-------|
| GET | `/health` | Health check |
| POST | `/auth/register` | Creates user |
| POST | `/auth/login` | Returns JWT |
| GET | `/auth/me` | Current user info |
| GET | `/transactions` | Paginated; search, type/category filters, sort |
| GET | `/transactions/categories` | Distinct categories for filters |
| POST | `/transactions` | Create (normalizes category) |
| PUT | `/transactions/{id}` | Update own transaction |
| DELETE | `/transactions/{id}` | Delete own transaction |
| GET/POST | `/budgets` | List / create |
| PUT/DELETE | `/budgets/{id}` | Update / delete |
| GET | `/budgets/progress` | Progress with case-insensitive matching |
| GET | `/dashboard` | Aggregated overview; optional `start_date` / `end_date` |

Transaction list query params: `page`, `page_size`, `sort_by`, `sort_order`, `search`, `type`, `category`

### Post-M8 polish (included above)

- Net Savings card removed; Balance / Income / Expenses only
- Full-height sidebar; Geist Sans typography
- Free-text category input (no autocomplete); sort controls removed from UI
- User-selectable `transaction_date` on create/edit
- Dashboard date selector removed; balance is all-time, income/expense are current month
- Dashboard widgets limited to 5 recent transactions and 5 highest-usage budgets
- Transaction edit dialog Select controlled-state fix

### Automated tests (M10)

| Module | Coverage |
|--------|----------|
| `test_auth.py` | Registration, login, password hashing, JWT protected routes |
| `test_transactions.py` | CRUD, category normalization, user isolation |
| `test_budgets.py` | CRUD, case-insensitive progress |
| `test_dashboard.py` | Balance aggregation, monthly filtering, widget limits |

Run from `backend/` with the virtual environment activated:

```bash
cd backend
python -m venv .venv   # first time only

# Activate (choose one):
# PowerShell:  .venv\Scripts\Activate.ps1
# CMD:         .venv\Scripts\activate.bat
# macOS/Linux: source .venv/bin/activate

pip install -r requirements-dev.txt
pytest
```

---

## What Is NOT Implemented

- Transaction detail view (single-transaction page)
- Category autocomplete (intentionally removed; free-text only)
- CI/CD pipeline
- Alembic migrations (production schema changes are manual when `APP_ENV=production`)
- Next.js middleware for server-side route protection
- Token refresh / rotation; httpOnly cookie storage
- Dedicated category database table
- Advanced dashboard analytics (goals, forecasts, etc.)
- Dashboard date range selector UI (removed; backend params remain)

---

## Key Files

```
finance-app/
├── PROJECT_STATUS.md
├── README.md
├── docker-compose.yml
├── .env.example
├── frontend/
│   ├── Dockerfile
│   ├── app/                    layout, login, register, (main) pages
│   ├── components/             auth, budgets, dashboard, layout, transactions, ui
│   └── lib/                    api, auth, format, types
└── backend/
    ├── Dockerfile
    ├── pytest.ini
    ├── requirements-dev.txt
    ├── tests/                  conftest + auth/transactions/budgets/dashboard tests
    └── app/
        ├── main.py
        ├── core/               config, auth, categories
        ├── api/routes/         auth, budgets, dashboard, transactions
        ├── services/           budget, dashboard
        ├── db/                 session, migrate
        ├── models/
        └── schemas/
```

---

## How to Run

### Full stack (Docker)

```bash
cd finance-app
cp .env.example .env   # first time only
docker compose up -d --build
```

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API docs: http://localhost:8000/docs

### Local frontend development

```bash
# Terminal 1 — database + backend
cd finance-app
docker compose up -d postgres backend

# Terminal 2 — frontend
cd finance-app/frontend
npm install
npm run dev
```

### Manual test checklist

1. Register at `/register`, sign in at `/login`
2. Create/edit/delete transactions with a custom date and free-text category
3. Use search, type/category filters, and pagination on `/transactions`
4. Create budgets on `/budgets`; verify progress updates
5. Open `/dashboard` — summary cards, top 5 budgets, 5 recent transactions, charts
6. Confirm sidebar spans full viewport height
7. Sign in as a second user — confirm data isolation

---

## Suggested Next Steps

1. CI/CD — wire pytest into GitHub Actions and deploy pipeline
2. Auth hardening — token refresh, httpOnly cookies, Next.js middleware
3. Alembic migrations — replace manual production schema provisioning
4. Category model — dedicated table with managed categories (optional)
