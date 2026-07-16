# Project Status

Living document tracking what has been built and what remains.

**Last updated:** July 16, 2026  
**Latest milestone:** M19 — Natural Language Financial Actions  
**Milestones completed:** 19 of 19

---

## Current Application Status

Production application is **live and verified**:

| | URL |
|---|---|
| Frontend | https://app.jakesfinancetracker.com |
| Backend API | https://api.jakesfinancetracker.com |
| Health check | https://api.jakesfinancetracker.com/health |

**Deployment:** AWS ECS Fargate (frontend + backend), Amazon RDS PostgreSQL, Application Load Balancers with ACM HTTPS, Route 53 DNS, Docker images in ECR, automated GitHub Actions CI/CD.

**Authentication:** httpOnly Secure JWT cookies — no client-side token storage.

**AI (when enabled):** Gemini-powered spending insights and natural language transaction/budget creation on the dashboard. API key is backend-only.

**Budgeting:** Progress bars reflect **current calendar month** expense spending only; resets automatically each month.

**Testing:** 68 backend integration tests (pytest).

**Design direction:** Clean, modern, calm, professional. Off-white backgrounds, soft green accents, Geist Sans typography.

---

## Vision

Personal finance management platform. Intended user flow:

1. User authenticates
2. Lands on a personalized financial dashboard
3. Views current financial information
4. Manages transactions and budgets
5. Uses AI insights and natural language actions (optional)
6. All data is isolated per authenticated user

---

## Milestone Progress

| Milestone | Status | Summary |
|-----------|--------|---------|
| M1 — Project foundation | Complete | Monorepo scaffold, Next.js + FastAPI + Docker Postgres |
| M2 — Pages, transactions, DB | Complete | UI shell, themed pages, transaction CRUD (create/view), DB connected |
| M3 — Authentication (JWT) | Complete | Register/login, JWT auth, protected routes, password hashing |
| M4 — User isolation | Complete | Transactions scoped to authenticated user via JWT |
| M5 — Budget CRUD | Complete | Budget model, CRUD API, monthly progress calculation, functional budgets page |
| M6 — Dashboard analytics | Complete | Live balance, monthly summary, budget progress, recent transactions, spending chart |
| M7 — Transaction management | Complete | Full transaction CRUD, filtering, category normalization, FK constraints |
| M8 — Dashboard and UX refinement | Complete | Income vs expense chart, pagination, loading/error states, `/auth/me` |
| M9 — Deployment and production readiness | Complete | Frontend Docker container, full-stack Compose, env docs, startup validation |
| M10 — Automated backend testing | Complete | pytest suite, isolated test database, auth/transaction/budget/dashboard coverage |
| M11 — Continuous integration | Complete | GitHub Actions CI: backend tests, frontend build, Docker validation |
| M12 — AWS deployment / production launch | Complete | ECS + ALB frontend/backend, RDS PostgreSQL, production env, verified live |
| M13 — Continuous deployment | Complete | GitHub Actions CD: push to `main` → ECR → ECS deploy, verified in production |
| M14 — UX polish | Complete | Custom 404 page consistent with the application's design system |
| M15 — HTTPS deployment | Complete | Custom domains, ACM certificates, ALB TLS, HTTPS CI/CD verification |
| M16 — Mobile responsiveness | Complete | Responsive layouts, mobile navigation, touch-friendly forms, page-level QA across all routes |
| M17 — Authentication hardening | Complete | httpOnly Secure cookies, cookie-only backend auth, `/auth/me` session validation, backend logout |
| M18 — AI Financial Insights | Complete | Gemini integration, authenticated `/ai/insights`, dashboard AI card, Markdown-formatted responses |
| M19 — Natural Language Financial Actions | Complete | Gemini intent parsing, transaction/budget creation via existing services, dashboard AI actions card, validation pipeline |

> **Note:** M3 originally used client-side JWT storage; M17 replaced this with httpOnly cookies. M5 progress calculation was refined post-M19 to use current-month `transaction_date` filtering (expenses only).

---

## What Is Implemented

### Core

| Area | Status | Details |
|------|--------|---------|
| **Authentication** | Complete | Register, login, logout, `GET /auth/me`; bcrypt password hashing |
| **Transactions** | Complete | Full CRUD, search, type/category filters, pagination, user-selected dates |
| **Budgets** | Complete | Full CRUD, progress bars, case-insensitive category matching |
| **Dashboard** | Complete | All-time balance; current-month income/expenses; top 5 budgets; 5 recent transactions; charts |
| **Categories** | Complete | Free-text categories normalized on write (trim + title case); no separate categories table |

#### Pages

| Route | Details |
|-------|---------|
| `/login` | Email/password; backend sets httpOnly cookie |
| `/register` | Email/password (min 8 chars) |
| `/dashboard` | Summary cards, charts, budget overview, recent transactions, AI insights & actions |
| `/transactions` | CRUD, filters, pagination; card layout mobile, table desktop |
| `/budgets` | CRUD, monthly progress bars, responsive card grid |
| `/health` | Public health check for ALB |
| `/*` | Custom 404 page |

#### API Endpoints

| Method | Endpoint | Notes |
|--------|----------|-------|
| GET | `/health` | Health check |
| POST | `/auth/register` | Creates user |
| POST | `/auth/login` | Sets httpOnly cookie |
| POST | `/auth/logout` | Clears cookie |
| GET | `/auth/me` | Current user |
| GET/POST/PUT/DELETE | `/transactions`, `/transactions/{id}` | CRUD + list with filters |
| GET | `/transactions/categories` | Distinct categories |
| GET/POST/PUT/DELETE | `/budgets`, `/budgets/{id}` | CRUD |
| GET | `/budgets/progress` | Current-month expense progress |
| GET | `/dashboard` | Aggregated overview |
| POST | `/ai/insights` | Gemini financial insights |
| POST | `/ai/action` | Natural language transaction/budget creation |

#### Models

| Model | Key fields |
|-------|------------|
| `User` | `id`, `email`, `hashed_password`, `created_at` |
| `Transaction` | `id`, `user_id`, `description`, `amount`, `type`, `category`, `transaction_date` |
| `Budget` | `id`, `user_id`, `category`, `limit_amount` |

---

### Infrastructure

- **Docker** — Compose stack: PostgreSQL 16, FastAPI, Next.js (health checks on all services)
- **PostgreSQL** — Local via Compose; production via Amazon RDS
- **ECS Fargate** — Separate services for frontend and backend
- **RDS** — Managed PostgreSQL in production
- **ALB** — HTTPS termination, health checks on `/health`
- **HTTPS / ACM** — TLS certificates on both load balancers; HTTP → HTTPS redirect
- **Route 53** — DNS for `app.jakesfinancetracker.com` and `api.jakesfinancetracker.com`
- **ECR** — Docker image registry
- **CI/CD** — GitHub Actions: CI on push/PR (`ci.yml`); CD on `main` after CI passes (`deploy.yml`)

Environment templates: `.env.example`, `.env.production.example`

---

### Security

- **httpOnly cookie authentication** — JWT not accessible to JavaScript
- **Secure logout** — `POST /auth/logout` clears cookie; frontend redirects to `/login`
- **Protected routes** — `AuthGuard` validates session via `GET /auth/me`; backend `get_current_user()` on all data routes
- **User isolation** — All queries filtered by authenticated `user_id`
- **Cross-subdomain cookies** — `COOKIE_DOMAIN=.jakesfinancetracker.com` in production
- **CORS** — Credentialed requests with explicit origin allowlist
- **AI key isolation** — `GEMINI_API_KEY` backend-only; never in frontend env vars

---

### Frontend

- Next.js 15 App Router, TypeScript, Tailwind CSS v4, shadcn/ui
- React Hook Form + Zod validation
- Recharts for dashboard visualizations
- Responsive design — hamburger navigation below `lg` (1024px), sidebar at desktop
- Loading skeletons, error states with retry, custom 404 page
- `AIInsightsCard` — Markdown-rendered Gemini insights (`react-markdown`)
- `AIActionsCard` — natural language input with loading, success, and error states
- Dashboard silent refresh after successful AI actions

---

### AI

| Feature | Endpoint | Details |
|---------|----------|---------|
| **Spending Insights** | `POST /ai/insights` | Sanitized aggregates → Gemini → Markdown response |
| **Natural Language Actions** | `POST /ai/action` | User message → Gemini JSON → validation → CRUD services |

- Gemini integration via `google-genai` (`ai_service.py`)
- Insights context built in `ai_insights_service.py` (no PII, no raw transaction descriptions)
- Action parsing in `ai_action_service.py` (relative dates, merchant/category mapping, income vs expense)
- AI never writes directly to database — uses `create_transaction_for_user()` and `create_budget_for_user()`
- Configurable via `AI_ENABLED`, `AI_PROVIDER`, `AI_MODEL`, `GEMINI_API_KEY`
- Tests mock Gemini; `AI_ENABLED=false` in test conftest

**Example natural language inputs:**
- "I spent $42 at Costco"
- "I got paid $1800"
- "Make a $250 grocery budget"
- "I paid $65 for gas yesterday"

---

### Budgeting

- Budgets represent **monthly spending limits**
- Progress sums **expense** transactions only
- Filtered to **current calendar month** by `transaction_date` (`>= month start`, `< next month start`)
- Category matching is case-insensitive
- Income transactions never count toward budget usage
- Progress resets to $0 on the first day of each new month until new expenses are recorded
- Implemented in `get_budget_progress_for_user()` (`backend/app/services/budget.py`)

---

### Testing

| Module | Coverage |
|--------|----------|
| `test_auth.py` | Registration, login, cookie auth, logout, protected routes |
| `test_transactions.py` | CRUD, category normalization, user isolation |
| `test_budgets.py` | CRUD, case-insensitive progress, current-month filtering |
| `test_dashboard.py` | Balance aggregation, monthly summary, budget overview, widget limits |
| `test_ai.py` | Insights, action parsing/validation/execution, mocked Gemini, error mapping |

**Total:** 68 integration tests against isolated `finance_app_test` database.

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
pytest
```

CI runs the same suite on every push/PR to `main`.

---

## What Is NOT Implemented

- Transaction detail view (single-transaction page)
- Category autocomplete (intentionally removed; free-text only)
- Alembic migrations (production schema changes manual when `APP_ENV=production`)
- Next.js middleware for server-side route protection
- Token refresh / rotation
- Dedicated category database table
- Advanced dashboard analytics (goals, forecasts)
- Dashboard date range selector UI (backend params remain)
- AI chat with conversation history
- Auto-refresh on `/transactions` and `/budgets` after AI actions (dashboard refreshes today)

---

## Key Files

```
/
├── README.md
├── PROJECT_STATUS.md
├── ARCHITECTURE_GUIDE.md
├── docker-compose.yml
├── frontend/
│   ├── app/                    Pages, layouts, auth routes
│   ├── components/             Dashboard (AI cards), budgets, transactions, UI
│   └── lib/                    api.ts, auth, types, format
├── backend/
│   ├── app/
│   │   ├── api/routes/         auth, transactions, budgets, dashboard, ai
│   │   ├── services/           budget, transaction, dashboard, ai_*
│   │   ├── models/             User, Transaction, Budget
│   │   └── schemas/            Pydantic request/response models
│   └── tests/                  68 pytest integration tests
└── .github/workflows/
    ├── ci.yml
    └── deploy.yml
```

---

## How to Run

```bash
cp .env.example .env
docker compose up -d --build
```

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API docs: http://localhost:8000/docs

### Manual test checklist

1. Register at `/register`, sign in at `/login`
2. Create/edit/delete transactions with custom date and category
3. Use search, filters, and pagination on `/transactions`
4. Create budgets on `/budgets`; verify monthly progress updates
5. Open `/dashboard` — summary cards, charts, AI insights and actions (if enabled)
6. Try "I spent $42 at Costco" in AI actions — confirm dashboard refresh
7. Sign in as a second user — confirm data isolation
8. Resize to 320px–1440px — confirm responsive layouts

---

## Suggested Next Steps

1. Alembic migrations — versioned, reversible schema changes
2. CD hardening — GitHub OIDC instead of long-lived AWS access keys
3. Token refresh and Next.js middleware
4. CloudWatch monitoring and alerts
