# Project Status

> Living document tracking what has been built and what remains.
> Last updated: Milestone 2 complete (July 2026).

## Vision

Personal finance management platform. Intended user flow:

1. User authenticates
2. Lands on a personalized financial dashboard
3. Views current financial information
4. Manages transactions and budgets
5. All data is isolated per authenticated user

**Design direction:** Clean, modern, calm, professional, minimal — off-white backgrounds, soft green accents, neutral text. Similar to modern personal finance apps.

---

## Milestone Progress

| Milestone | Status | Summary |
|-----------|--------|---------|
| M1 — Project foundation | ✅ Complete | Monorepo scaffold, Next.js + FastAPI + Docker Postgres |
| M2 — Pages, transactions, DB | ✅ Complete | UI shell, themed pages, transaction CRUD (create/view), DB connected |
| M3 — Authentication (JWT) | ❌ Not started | Login, registration, token-based auth |
| M4 — User isolation | ❌ Not started | Real per-user data ownership |
| M5 — Budget CRUD | ❌ Not started | Full budget management |
| M6 — Dashboard analytics | ❌ Not started | Live calculations, charts, trends |

---

## What Is Implemented

### Infrastructure

- [x] Monorepo layout (`frontend/`, `backend/`, root config)
- [x] Docker Compose: PostgreSQL 16 (persistent volume, health check)
- [x] Docker Compose: FastAPI backend service
- [x] Environment config (`.env.example`, `CORS_ORIGINS`, `DATABASE_URL`, `NEXT_PUBLIC_API_URL`)
- [x] Root `.gitignore`

### Frontend

- [x] Next.js 15 (App Router, TypeScript, Tailwind CSS v4)
- [x] shadcn/ui (base-nova style) — Button, Card, Input, Label, Select, Table, Badge, Separator
- [x] React Hook Form + Zod (used on transactions form)
- [x] Lucide React icons
- [x] Recharts installed (not yet used in UI)
- [x] Off-white / soft-green theme in `globals.css`
- [x] App shell with sidebar navigation (`AppShell`, `SidebarNav`)
- [x] Route group `(main)` wrapping authenticated-style pages
- [x] Root `/` redirects to `/dashboard`
- [x] API client (`lib/api.ts`) and shared types (`lib/types.ts`)

#### Pages

| Route | Status | Details |
|-------|--------|---------|
| `/dashboard` | Placeholder UI | Widget layout for balance, income/expense summaries, budget progress, recent transactions, trends chart area — all show `—` or empty states |
| `/transactions` | **Functional** | Create form + transaction table, connected to backend, refreshes after add |
| `/budgets` | Placeholder UI | Static skeleton cards (Groceries, Transportation, etc.) with no data or actions |

### Backend

- [x] FastAPI app with CORS middleware
- [x] Health endpoint: `GET /health`
- [x] SQLAlchemy 2.x engine + session (`db/session.py`, `db/base.py`)
- [x] Config from environment (`core/config.py`)
- [x] Auto table creation on startup (`Base.metadata.create_all`)
- [x] Package structure: `api/`, `core/`, `models/`, `schemas/`, `services/`, `db/`
- [x] Empty `services/` package (reserved for business logic)

#### Models

| Model | Status | Fields |
|-------|--------|--------|
| `Transaction` | ✅ Active | `id`, `user_id`, `description`, `amount`, `type` (income/expense), `category`, `created_at` |
| `User` | Placeholder | `id`, `email` — table exists, not used by auth yet |

#### API Endpoints

| Method | Endpoint | Status |
|--------|----------|--------|
| GET | `/health` | ✅ Working |
| GET | `/transactions` | ✅ Working — filtered by placeholder `user_id` |
| POST | `/transactions` | ✅ Working — assigns placeholder `user_id` |

#### Auth (preparation only)

- [x] `core/auth.py` with `get_current_user_id()` returning fixed `DEFAULT_USER_ID = 1`
- [x] All transaction queries filter by `user_id`
- [x] `python-jose` and `passlib[bcrypt]` installed but unused
- [ ] JWT issuance, validation, login/register routes

### Database

- [x] PostgreSQL connected from backend
- [x] `transactions` table with correct schema and `user_id` index
- [x] `users` table created (placeholder)
- [ ] Alembic migrations (dependency installed, not configured)
- [ ] Seed data or migration scripts

---

## What Is NOT Implemented

### Authentication & Users

- [ ] Login / registration pages
- [ ] JWT token generation and validation
- [ ] Protected routes on frontend
- [ ] Auth middleware / dependencies on backend
- [ ] Password hashing flow
- [ ] Real user creation and session management
- [ ] Per-user data isolation (currently all data uses `user_id = 1`)

### Transactions (remaining)

- [ ] Edit transaction
- [ ] Delete transaction
- [ ] Transaction filtering, search, pagination
- [ ] Transaction detail view

### Budgets

- [ ] Budget model and database table
- [ ] Budget API endpoints (CRUD)
- [ ] Budget create/edit/delete UI
- [ ] Budget progress calculations
- [ ] Linking transactions to budgets

### Dashboard

- [ ] Real balance calculation
- [ ] Income / expense summaries from transaction data
- [ ] Budget progress from live data
- [ ] Recent transactions widget (pulls from API)
- [ ] Financial trends chart (Recharts)
- [ ] Date range filtering

### General / Infrastructure

- [ ] Frontend Docker service in Compose
- [ ] Alembic migration setup
- [ ] API error handling standards
- [ ] Unit / integration tests
- [ ] CI/CD pipeline
- [ ] Production deployment config

---

## Key Files Reference

```
finance-app/
├── PROJECT_STATUS.md          ← this file
├── README.md                  ← setup and run instructions
├── docker-compose.yml         ← postgres + backend
├── .env.example
│
├── frontend/
│   ├── app/(main)/
│   │   ├── layout.tsx         ← AppShell wrapper
│   │   ├── dashboard/page.tsx
│   │   ├── transactions/page.tsx
│   │   └── budgets/page.tsx
│   ├── components/
│   │   ├── layout/            ← sidebar + shell
│   │   ├── dashboard/         ← placeholder widgets
│   │   └── transactions/      ← form + list (functional)
│   └── lib/
│       ├── api.ts             ← backend HTTP client
│       └── types.ts
│
└── backend/
    ├── Dockerfile
    └── app/
        ├── main.py            ← FastAPI entry, CORS, lifespan
        ├── core/
        │   ├── config.py
        │   └── auth.py        ← placeholder user ID
        ├── api/routes/transactions.py
        ├── models/transaction.py
        └── schemas/transaction.py
```

---

## How to Run (current state)

```bash
# Terminal 1 — database + backend
cd finance-app
docker compose up -d --build

# Terminal 2 — frontend
cd finance-app/frontend
npm run dev
```

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API docs: http://localhost:8000/docs

---

## Suggested Next Steps (Milestone 3+)

1. **Authentication** — JWT login/register, protect routes, replace `DEFAULT_USER_ID`
2. **Transaction edit/delete** — `PUT/PATCH` and `DELETE` endpoints + UI
3. **Budget model + CRUD** — backend model, API, functional budgets page
4. **Dashboard wiring** — aggregate transaction data into dashboard widgets
5. **Alembic migrations** — replace `create_all` with versioned migrations
