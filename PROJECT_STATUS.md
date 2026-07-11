# Project Status

Living document tracking what has been built and what remains.

Last updated: July 11, 2026

**Current state:** Full-stack personal finance app live on AWS ECS Fargate with RDS PostgreSQL. GitHub Actions CI/CD deploys automatically on push to `main`. Application is HTTPS-ready at the code level; ALB HTTPS termination requires manual AWS configuration (see README HTTPS Deployment Checklist).

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
| M11 — Continuous integration | Complete | GitHub Actions CI: backend tests, frontend build, Docker validation |
| M12 — AWS deployment / production launch | Complete | ECS + ALB frontend/backend, RDS PostgreSQL, production env, verified live |
| M13 — Continuous deployment | Complete | GitHub Actions CD: push to `main` → ECR → ECS deploy, verified in production |
| M14 — UX polish | Complete | Custom 404 page consistent with the application's design system |

---

## What Is Implemented

### Infrastructure

- Repository layout (`frontend/`, `backend/`, root config)
- Docker Compose: PostgreSQL 16, FastAPI backend, Next.js frontend (all with health checks)
- Environment config (`.env.example`, `.env.production.example`, `APP_ENV`, `CORS_ORIGINS`, `DATABASE_URL`, `SECRET_KEY`, `NEXT_PUBLIC_API_URL`, `COOKIE_SECURE`, `COOKIE_SAMESITE`, `COOKIE_HTTPONLY`, `TEST_DATABASE_URL`)
- HTTPS-ready configuration: production URLs require `https://`; local development uses HTTP
- CORS credentialed requests enabled (`allow_credentials=True`) for future cookie-based auth
- Cookie security flags environment-driven (`backend/app/core/cookies.py`)
- Production Dockerfiles with health checks and startup validation
- Production startup skips automatic schema changes (`APP_ENV=production`)
- Startup validation for required config and database connectivity
- Structured logging on backend startup and shutdown
- GitHub Actions CI (`.github/workflows/ci.yml`) on push/PR to `main`
- GitHub Actions CD (`.github/workflows/deploy.yml`) on push to `main` after CI passes
- AWS production deployment (ECS Fargate, ALB, RDS PostgreSQL, ECR)

### Frontend

- Next.js 15 (App Router, TypeScript, Tailwind CSS v4)
- shadcn/ui, React Hook Form + Zod, Lucide React, Recharts
- Off-white / soft-green theme; Geist Sans via `next/font`
- Full-height sidebar app shell; authenticated routes behind `AuthGuard`
- Login and registration pages; JWT stored in `localStorage` (httpOnly cookie migration planned)
- API client sends `credentials: "include"` on all requests
- Loading skeletons and error states with retry
- Health endpoint: `GET /health` (public, no auth; used by ALB target group)
- Custom 404 page (`app/not-found.tsx`) matching app design system

#### Pages

| Route | Status | Details |
|-------|--------|---------|
| `/login` | Functional | Email/password form, stores JWT, redirects to dashboard |
| `/register` | Functional | Email/password registration (min 8 chars), redirects to login |
| `/dashboard` | Functional | All-time balance; current-month income/expenses; top 5 budgets by usage; 5 recent transactions; charts |
| `/transactions` | Functional | Create/edit/delete with user-selected date; free-text category; search, type/category filters, pagination |
| `/budgets` | Functional | Add/edit/delete budgets, progress bars, loading/error states |
| `/health` | Functional | Public health check; returns `{"status":"ok"}` for ALB |
| `/*` (unknown routes) | Functional | Custom 404 page via `app/not-found.tsx` |

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

### UX polish (M14)

- Custom 404 page (`app/not-found.tsx`) with centered layout, app branding, and navigation to dashboard/login
- Frontend `GET /health` endpoint added for ALB target group health checks
- ALB target group health checks configured to use `/health` on frontend and backend

### HTTPS readiness

Application code is prepared for HTTPS. Remaining work is manual AWS configuration.

| Item | Status |
|------|--------|
| Production env templates use `https://` URLs | Ready |
| Backend validates HTTPS CORS origins in production | Ready |
| Cookie security flags (`COOKIE_SECURE`, `COOKIE_SAMESITE`) | Configured |
| Frontend `credentials: "include"` on API requests | Ready |
| ALB HTTPS listener + ACM certificate | Pending (manual AWS) |
| HTTP → HTTPS redirect on ALB | Pending (manual AWS) |
| JWT httpOnly cookie storage | Planned (auth hardening) |

See [README.md](./README.md#https-deployment-checklist) for the full HTTPS deployment checklist.

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

### AWS deployment / production launch (M12)

Application is live in AWS production. Both ECS services are running and verified.

| Item | Status |
|------|--------|
| Frontend on AWS ECS Fargate behind Application Load Balancer | Running |
| Backend on AWS ECS Fargate behind Application Load Balancer | Running |
| PostgreSQL on AWS RDS | Running |
| Docker images in Amazon ECR | Active |
| ECS services running | Verified |
| Frontend and backend communicating | Verified |
| Database persistence | Verified |
| Backend `APP_ENV` set to `production` | Configured |
| Production environment variables via ECS | Configured |
| End-to-end production verification | Verified |

Production configuration:

- Backend runs with `APP_ENV=production` (no automatic schema changes on startup)
- Environment variables (`DATABASE_URL`, `SECRET_KEY`, `CORS_ORIGINS`, etc.) set through ECS task definitions
- Frontend image built with production `NEXT_PUBLIC_API_URL` pointing to the backend ALB URL
- Health checks: backend `GET /health`; frontend `GET /health` (ALB target group)

See [README.md](./README.md#aws-deployment) for deployment architecture and troubleshooting.

### Continuous integration and deployment (M11 + M13)

Full CI/CD pipeline is operational. Pushing to `main` triggers validation and production deployment.

**CI** — [`.github/workflows/ci.yml`](.github/workflows/ci.yml)

Runs on every push and pull request to `main`. Three parallel jobs:

| Job | Validates |
|-----|-----------|
| Backend Tests | pytest against PostgreSQL service (Python 3.12) |
| Frontend Build | `npm ci`, ESLint, production `npm run build` (Node 20) |
| Docker Validation | Backend and frontend image builds; `docker compose config` |

**CD** — [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml)

Runs automatically after CI succeeds on `main` push, or manually via **Actions → Deploy → Run workflow**.

| Step | Action |
|------|--------|
| Trigger | CI success on `main` push, or manual `workflow_dispatch` |
| Build | Backend and frontend Docker images tagged with commit SHA |
| Push | Images published to Amazon ECR |
| Deploy | ECS task definitions updated; services rolled out |
| Verify | Backend `/health` and frontend availability checked |

Current production state:

- Push to `main` → CI passes → CD deploys to ECS
- ALB target group health checks use `/health` on both frontend and backend
- Production deployment verified working

See [README.md](./README.md#continuous-integration) and [README.md](./README.md#continuous-deployment) for details.

---

## What Is NOT Implemented

- Transaction detail view (single-transaction page)
- Category autocomplete (intentionally removed; free-text only)
- Alembic migrations (production schema changes are manual when `APP_ENV=production`)
- ALB HTTPS termination (ACM certificate, HTTPS listener, HTTP redirect) — manual AWS steps documented
- Next.js middleware for server-side route protection
- Token refresh / rotation; httpOnly cookie storage
- Dedicated category database table
- Advanced dashboard analytics (goals, forecasts, etc.)
- Dashboard date range selector UI (removed; backend params remain)

---

## Key Files

```
/
├── PROJECT_STATUS.md
├── README.md
├── docker-compose.yml
├── .env.example
├── .env.production.example
├── frontend/
│   ├── Dockerfile
│   ├── app/                    layout, login, register, (main) pages, /health, not-found
│   ├── components/             auth, budgets, dashboard, layout, transactions, ui
│   └── lib/                    api, auth, format, types
├── backend/
│   ├── Dockerfile
│   ├── pytest.ini
│   ├── requirements-dev.txt
│   ├── tests/                  conftest + auth/transactions/budgets/dashboard tests
│   └── app/
│       ├── main.py
│       ├── core/               config, auth, categories, cookies
│       ├── api/routes/         auth, budgets, dashboard, transactions
│       ├── services/           budget, dashboard
│       ├── db/                 session, migrate
│       ├── models/
│       └── schemas/
└── .github/workflows/
    ├── ci.yml                  GitHub Actions CI pipeline
    └── deploy.yml              GitHub Actions CD pipeline
```

## How to Run

### Full stack (Docker)

```bash
cp .env.example .env   # first time only
docker compose up -d --build
```

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API docs: http://localhost:8000/docs

### Local frontend development

```bash
# Terminal 1 — database + backend
docker compose up -d postgres backend

# Terminal 2 — frontend
cd frontend
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

1. Enable HTTPS on ALB — ACM certificate, HTTPS listener, HTTP redirect (see README checklist)
2. Auth hardening — migrate JWT to httpOnly Secure cookies, token refresh, Next.js middleware
3. Alembic migrations — replace manual production schema provisioning
4. Category model — dedicated table with managed categories (optional)
5. CD hardening — GitHub OIDC instead of long-lived AWS access keys; deployment approval gates
