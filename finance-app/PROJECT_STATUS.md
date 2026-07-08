# Project Status

> Living document tracking what has been built and what remains.
> Last updated: Milestone 7 complete (July 2026).

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
| M6 — Dashboard analytics | ✅ Complete | Live balance, monthly summary, budget progress, recent transactions, spending chart |
| M7 — Transaction management | ✅ Complete | Full transaction CRUD, filtering, category normalization, FK constraints |

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
- [x] Recharts (used on dashboard spending trends chart)
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
| `/dashboard` | **Functional** | Protected — live balance, monthly income/expenses, budget progress, recent transactions, 6-month spending chart |
| `/transactions` | **Functional** | Protected — create/edit/delete transactions, search and filter (type, category), responsive table |
| `/budgets` | **Functional** | Protected — add/edit/delete budgets, progress bars from live transaction data |

### Backend

- [x] FastAPI app with CORS middleware
- [x] Health endpoint: `GET /health`
- [x] SQLAlchemy 2.x engine + session (`db/session.py`, `db/base.py`)
- [x] Config from environment (`core/config.py`) — includes `SECRET_KEY`, `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`
- [x] Auto table creation on startup (`Base.metadata.create_all`)
- [x] Lightweight startup migrations (`db/migrate.py`) — users columns, foreign keys
- [x] Package structure: `api/`, `core/`, `models/`, `schemas/`, `services/`, `db/`
- [x] Business logic in `services/` — budget progress and dashboard aggregation
- [x] Category normalization (`core/categories.py`) — trim + title case on save, case-insensitive budget matching

#### Models

| Model | Status | Fields |
|-------|--------|--------|
| `Transaction` | ✅ Active | `id`, `user_id` (FK → users, CASCADE), `description`, `amount`, `type`, `category`, `created_at` |
| `User` | ✅ Active | `id`, `email` (unique, indexed), `hashed_password`, `created_at` |
| `Budget` | ✅ Active | `id`, `user_id` (FK → users, CASCADE), `category`, `limit_amount`, `created_at`, `updated_at` |

#### API Endpoints

| Method | Endpoint | Status |
|--------|----------|--------|
| GET | `/health` | ✅ Working |
| POST | `/auth/register` | ✅ Working — creates user, returns safe user info (no password hash) |
| POST | `/auth/login` | ✅ Working — returns JWT `{ access_token, token_type: "bearer" }` |
| GET | `/transactions` | ✅ Working — requires auth, returns current user's transactions only |
| POST | `/transactions` | ✅ Working — requires auth, normalizes category on save |
| PUT | `/transactions/{id}` | ✅ Working — requires auth, updates user's own transaction |
| DELETE | `/transactions/{id}` | ✅ Working — requires auth, deletes user's own transaction |
| GET | `/budgets` | ✅ Working — requires auth, returns current user's budgets |
| POST | `/budgets` | ✅ Working — requires auth, normalizes category on save |
| PUT | `/budgets/{id}` | ✅ Working — requires auth, updates user's own budget |
| DELETE | `/budgets/{id}` | ✅ Working — requires auth, deletes user's own budget |
| GET | `/budgets/progress` | ✅ Working — case-insensitive category matching for spent totals |
| GET | `/dashboard` | ✅ Working — aggregated financial overview for authenticated user |

#### Authentication

- [x] Password hashing via passlib + bcrypt (`bcrypt==4.0.1` pinned for compatibility)
- [x] JWT creation and validation (`python-jose`)
- [x] `get_current_user` FastAPI dependency — reads `Authorization: Bearer <token>`
- [x] All data routes protected and scoped to authenticated user
- [x] Pydantic schemas: `UserCreate`, `LoginRequest`, `TokenResponse`, `UserResponse`, `TransactionUpdate`, `DashboardResponse`

### Database

- [x] PostgreSQL connected from backend
- [x] `transactions` table with `user_id` FK → `users.id` ON DELETE CASCADE
- [x] `users` table with auth fields (`email`, `hashed_password`, `created_at`)
- [x] `budgets` table with `user_id` FK → `users.id` ON DELETE CASCADE
- [x] Startup migration adds missing auth columns and foreign keys to legacy databases

---

## What Is NOT Implemented

### Transactions (remaining polish)

- [ ] Server-side filtering, search, pagination
- [ ] Transaction detail view

### Dashboard (remaining polish)

- [ ] Date range filtering for dashboard metrics
- [ ] Income vs expense comparison chart (currently expenses-only trend)

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
- [ ] Dedicated category table / autocomplete
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
│   │   ├── budgets/           ← form, card, edit dialog
│   │   ├── dashboard/         ← summary cards, budget widget, recent tx, chart
│   │   ├── layout/            ← sidebar + shell
│   │   └── transactions/      ← form, list, filters, edit dialog
│   └── lib/
│       ├── api.ts             ← backend HTTP client
│       ├── auth.ts            ← JWT storage and helpers
│       ├── format.ts          ← currency/date formatting
│       └── types.ts
│
└── backend/
    ├── Dockerfile
    └── app/
        ├── main.py            ← FastAPI entry, CORS, lifespan, migrations
        ├── core/
        │   ├── config.py
        │   ├── auth.py
        │   └── categories.py  ← category normalization
        ├── api/routes/
        │   ├── auth.py
        │   ├── budgets.py
        │   ├── dashboard.py
        │   └── transactions.py
        ├── services/
        │   ├── budget.py
        │   └── dashboard.py
        ├── db/migrate.py
        ├── models/
        └── schemas/
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

### Testing transactions

1. Sign in at `/login`
2. Add transactions on `/transactions`
3. Edit or delete using row actions
4. Use search and filters (type, category)
5. Verify `/dashboard` and `/budgets` reflect changes

---

## Suggested Next Steps

1. **Dashboard polish** — date range filters, income vs expense chart
2. **Server-side transaction filtering** — pagination for large datasets
3. **Category autocomplete** — suggest existing categories on create/edit
