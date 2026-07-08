# Project Status

> Living document tracking what has been built and what remains.
> Last updated: Milestone 5 complete (July 2026).

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
| M3 — Authentication (JWT) | ✅ Complete | Register/login, JWT auth, protected routes, password hashing |
| M4 — User isolation | ✅ Complete | Transactions scoped to authenticated user via JWT |
| M5 — Budget CRUD | ✅ Complete | Budget model, CRUD API, progress calculation, functional budgets page |
| M6 — Dashboard analytics | ❌ Not started | Live calculations, charts, trends |

---

## What Is Implemented

### Infrastructure

- [x] Monorepo layout (`frontend/`, `backend/`, root config)
- [x] Docker Compose: PostgreSQL 16 (persistent volume, health check)
- [x] Docker Compose: FastAPI backend service
- [x] Environment config (`.env.example`, `CORS_ORIGINS`, `DATABASE_URL`, `SECRET_KEY`, `NEXT_PUBLIC_API_URL`)
- [x] Root `.gitignore`

### Frontend

- [x] Next.js 15 (App Router, TypeScript, Tailwind CSS v4)
- [x] shadcn/ui (base-nova style) — Button, Card, Input, Label, Select, Table, Badge, Separator
- [x] React Hook Form + Zod (used on transactions and budgets forms)
- [x] Lucide React icons
- [x] Recharts installed (not yet used in UI)
- [x] Off-white / soft-green theme in `globals.css`
- [x] App shell with sidebar navigation (`AppShell`, `SidebarNav`)
- [x] Route group `(main)` wrapping authenticated pages behind `AuthGuard`
- [x] Root `/` redirects to `/dashboard`
- [x] API client (`lib/api.ts`) and shared types (`lib/types.ts`)
- [x] Auth state management (`lib/auth.ts`) — JWT + email in `localStorage`
- [x] Login and registration pages (`/login`, `/register`)
- [x] Sidebar logout button and signed-in email display

#### Pages

| Route | Status | Details |
|-------|--------|---------|
| `/login` | **Functional** | Email/password form, stores JWT on success, redirects to dashboard |
| `/register` | **Functional** | Email/password registration (min 8 chars), redirects to login |
| `/dashboard` | Placeholder UI | Protected — widget layout for balance, income/expense summaries, budget progress, recent transactions, trends chart area — all show `—` or empty states |
| `/transactions` | **Functional** | Protected — create form + transaction table, authenticated API calls, refreshes after add |
| `/budgets` | **Functional** | Protected — add/edit/delete budgets, progress bars from live transaction data |

### Backend

- [x] FastAPI app with CORS middleware
- [x] Health endpoint: `GET /health`
- [x] SQLAlchemy 2.x engine + session (`db/session.py`, `db/base.py`)
- [x] Config from environment (`core/config.py`) — includes `SECRET_KEY`, `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`
- [x] Auto table creation on startup (`Base.metadata.create_all`)
- [x] Lightweight legacy migration for `users` table columns (`db/migrate.py`)
- [x] Package structure: `api/`, `core/`, `models/`, `schemas/`, `services/`, `db/`
- [x] Empty `services/` package (reserved for business logic)

#### Models

| Model | Status | Fields |
|-------|--------|--------|
| `Transaction` | ✅ Active | `id`, `user_id`, `description`, `amount`, `type` (income/expense), `category`, `created_at` |
| `User` | ✅ Active | `id`, `email` (unique, indexed), `hashed_password`, `created_at` |
| `Budget` | ✅ Active | `id`, `user_id`, `category`, `limit_amount`, `created_at`, `updated_at` |

#### API Endpoints

| Method | Endpoint | Status |
|--------|----------|--------|
| GET | `/health` | ✅ Working |
| POST | `/auth/register` | ✅ Working — creates user, returns safe user info (no password hash) |
| POST | `/auth/login` | ✅ Working — returns JWT `{ access_token, token_type: "bearer" }` |
| GET | `/transactions` | ✅ Working — requires auth, returns current user's transactions only |
| POST | `/transactions` | ✅ Working — requires auth, assigns authenticated user's ID |
| GET | `/budgets` | ✅ Working — requires auth, returns current user's budgets |
| POST | `/budgets` | ✅ Working — requires auth, creates budget for current user |
| PUT | `/budgets/{id}` | ✅ Working — requires auth, updates user's own budget |
| DELETE | `/budgets/{id}` | ✅ Working — requires auth, deletes user's own budget |
| GET | `/budgets/progress` | ✅ Working — requires auth, calculates spent/remaining/percentage from expense transactions matched by category |

#### Authentication

- [x] Password hashing via passlib + bcrypt (`bcrypt==4.0.1` pinned for compatibility)
- [x] JWT creation and validation (`python-jose`)
- [x] `get_current_user` FastAPI dependency — reads `Authorization: Bearer <token>`
- [x] Transaction and budget routes protected and scoped to authenticated user
- [x] Pydantic schemas: `UserCreate`, `LoginRequest`, `TokenResponse`, `UserResponse`

### Database

- [x] PostgreSQL connected from backend
- [x] `transactions` table with correct schema and `user_id` index
- [x] `users` table with auth fields (`email`, `hashed_password`, `created_at`)
- [x] `budgets` table with `user_id` index, `category`, `limit_amount`, timestamps
- [x] Startup migration adds missing auth columns to legacy `users` tables
- [ ] Foreign key constraints (`transactions.user_id`, `budgets.user_id` → `users.id`)

---

## What Is NOT Implemented

### Transactions (remaining)

- [ ] Edit transaction
- [ ] Delete transaction
- [ ] Transaction filtering, search, pagination
- [ ] Transaction detail view

### Dashboard

- [ ] Real balance calculation
- [ ] Income / expense summaries from transaction data
- [ ] Budget progress widget (pulls from `/budgets/progress`)
- [ ] Recent transactions widget (pulls from API)
- [ ] Financial trends chart (Recharts)
- [ ] Date range filtering

### General / Infrastructure

- [ ] Frontend Docker service in Compose
- [ ] Unit / integration tests
- [ ] CI/CD pipeline

### Future polish (deferred)

- [ ] Next.js middleware for server-side route protection
- [ ] `/auth/me` endpoint
- [ ] Token refresh / rotation
- [ ] httpOnly cookie storage
- [ ] Alembic migrations
- [ ] Category normalization
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
│   ├── app/
│   │   ├── (main)/
│   │   │   ├── layout.tsx     ← AuthGuard + AppShell wrapper
│   │   │   ├── dashboard/page.tsx
│   │   │   ├── transactions/page.tsx
│   │   │   └── budgets/page.tsx
│   │   ├── login/page.tsx
│   │   └── register/page.tsx
│   ├── components/
│   │   ├── auth/auth-guard.tsx
│   │   ├── budgets/           ← form, card, edit dialog (functional)
│   │   ├── layout/            ← sidebar + shell
│   │   ├── dashboard/         ← placeholder widgets
│   │   └── transactions/      ← form + list (functional)
│   └── lib/
│       ├── api.ts             ← backend HTTP client (auth, transactions, budgets)
│       ├── auth.ts            ← JWT storage and helpers
│       └── types.ts
│
└── backend/
    ├── Dockerfile
    └── app/
        ├── main.py            ← FastAPI entry, CORS, lifespan, migration
        ├── core/
        │   ├── config.py      ← settings incl. JWT config
        │   └── auth.py        ← hashing, JWT, get_current_user
        ├── api/
        │   ├── router.py      ← registers auth, budgets, transactions routers
        │   ├── deps.py
        │   └── routes/
        │       ├── auth.py
        │       ├── budgets.py   ← CRUD + progress
        │       └── transactions.py
        ├── db/
        │   └── migrate.py     ← legacy users table column migration
        ├── models/
        │   ├── user.py
        │   ├── budget.py
        │   └── transaction.py
        └── schemas/
            ├── user.py
            ├── budget.py
            └── transaction.py
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

### Testing budgets

1. Sign in at `/login`
2. Go to `/budgets` and add a budget (e.g. Groceries, $500)
3. Add expense transactions on `/transactions` with matching category (e.g. Groceries)
4. Return to `/budgets` — spent, remaining, and progress bar update from transaction data
5. Edit or delete budgets using the card actions

**API quick test:**

```bash
# Login (save the access_token)
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@test.com","password":"password123"}'

# Create budget
curl -X POST http://localhost:8000/budgets \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"category":"Groceries","limit_amount":500.00}'

# Get progress
curl http://localhost:8000/budgets/progress \
  -H "Authorization: Bearer <access_token>"
```

---

## Suggested Next Steps (Milestone 6+)

1. **Dashboard wiring** — aggregate transaction and budget data into dashboard widgets
2. **Transaction edit/delete** — `PUT/PATCH` and `DELETE` endpoints + UI
3. **Financial trends chart** — wire Recharts to transaction history
