# Project Status

> Living document tracking what has been built and what remains.
> Last updated: Milestone 3 complete (July 2026).

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
| M5 — Budget CRUD | ❌ Not started | Full budget management |
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
- [x] React Hook Form + Zod (used on transactions form)
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
| `/budgets` | Placeholder UI | Protected — static skeleton cards (Groceries, Transportation, etc.) with no data or actions |

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

#### API Endpoints

| Method | Endpoint | Status |
|--------|----------|--------|
| GET | `/health` | ✅ Working |
| POST | `/auth/register` | ✅ Working — creates user, returns safe user info (no password hash) |
| POST | `/auth/login` | ✅ Working — returns JWT `{ access_token, token_type: "bearer" }` |
| GET | `/transactions` | ✅ Working — requires auth, returns current user's transactions only |
| POST | `/transactions` | ✅ Working — requires auth, assigns authenticated user's ID |

#### Authentication

- [x] Password hashing via passlib + bcrypt (`bcrypt==4.0.1` pinned for compatibility)
- [x] JWT creation and validation (`python-jose`)
- [x] `get_current_user` FastAPI dependency — reads `Authorization: Bearer <token>`
- [x] Transaction routes protected and scoped to authenticated user
- [x] Pydantic schemas: `UserCreate`, `LoginRequest`, `TokenResponse`, `UserResponse`
- [ ] `/auth/me` endpoint (email currently stored client-side after login)
- [ ] Token refresh flow
- [ ] httpOnly cookie-based auth (currently localStorage JWT)

### Database

- [x] PostgreSQL connected from backend
- [x] `transactions` table with correct schema and `user_id` index
- [x] `users` table with auth fields (`email`, `hashed_password`, `created_at`)
- [x] Startup migration adds missing auth columns to legacy `users` tables
- [ ] Alembic migrations (dependency installed, not configured)
- [ ] Foreign key constraint from `transactions.user_id` → `users.id`
- [ ] Seed data scripts

---

## What Is NOT Implemented

### Authentication (remaining polish)

- [ ] Next.js middleware for server-side route protection (currently client-side `AuthGuard` only)
- [ ] `/auth/me` endpoint for fetching current user profile
- [ ] Token refresh / rotation
- [ ] httpOnly cookie storage (more secure than localStorage)

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
- [ ] Alembic migration setup (replace `create_all` + ad-hoc column migration)
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
│   │   ├── layout/            ← sidebar + shell
│   │   ├── dashboard/         ← placeholder widgets
│   │   └── transactions/      ← form + list (functional)
│   └── lib/
│       ├── api.ts             ← backend HTTP client (auth + transactions)
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
        │   ├── router.py      ← registers auth + transactions routers
        │   ├── deps.py
        │   └── routes/
        │       ├── auth.py    ← register, login
        │       └── transactions.py
        ├── db/
        │   └── migrate.py     ← legacy users table column migration
        ├── models/
        │   ├── user.py
        │   └── transaction.py
        └── schemas/
            ├── user.py
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

### Testing authentication

1. Visit http://localhost:3000 — unauthenticated users are redirected to `/login`
2. Register a user at `/register` (password must be at least 8 characters)
3. Sign in at `/login` — JWT is stored and used for all API calls
4. Create transactions on `/transactions` — only visible to the signed-in user
5. Log out from the sidebar — token is cleared, redirected to `/login`

**API quick test:**

```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@test.com","password":"password123"}'

# Login (save the access_token)
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@test.com","password":"password123"}'

# Authenticated request
curl http://localhost:8000/transactions \
  -H "Authorization: Bearer <access_token>"
```

**Clean database reset** (if upgrading from pre-auth schema):

```bash
docker compose down -v
docker compose up -d --build
```

---

## Suggested Next Steps (Milestone 5+)

1. **Transaction edit/delete** — `PUT/PATCH` and `DELETE` endpoints + UI
2. **Budget model + CRUD** — backend model, API, functional budgets page
3. **Dashboard wiring** — aggregate transaction data into dashboard widgets
4. **Alembic migrations** — replace `create_all` with versioned migrations
5. **Auth polish** — `/auth/me` endpoint, httpOnly cookies, Next.js middleware
