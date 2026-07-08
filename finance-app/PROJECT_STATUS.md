# Project Status

> Living document tracking what has been built and what remains.
> Last updated: Milestone 8 complete (July 2026).

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
| M8 — Dashboard & UX refinement | ✅ Complete | Income vs expense chart, date filters, pagination/sorting, autocomplete, loading/error states, `/auth/me` |

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
- [x] shadcn/ui (base-nova style) — Button, Card, Input, Label, Select, Table, Badge, Separator, Skeleton
- [x] React Hook Form + Zod (used on transactions and budgets forms)
- [x] Lucide React icons
- [x] Recharts (spending trends chart + income vs expense comparison chart)
- [x] Off-white / soft-green theme in `globals.css`
- [x] App shell with sidebar navigation (`AppShell`, `SidebarNav`)
- [x] Route group `(main)` wrapping authenticated pages behind `AuthGuard`
- [x] Root `/` redirects to `/dashboard`
- [x] API client (`lib/api.ts`) and shared types (`lib/types.ts`)
- [x] Auth state management (`lib/auth.ts`) — JWT + email in `localStorage`
- [x] Login and registration pages (`/login`, `/register`)
- [x] Sidebar logout button; email from `/auth/me` (synced to localStorage)
- [x] Loading skeletons and error states with retry (`components/ui/skeleton.tsx`, `error-state.tsx`)
- [x] Date range presets for dashboard (`lib/date-range.ts`)
- [x] Category autocomplete from user history + common categories (`lib/categories.ts`)

#### Pages

| Route | Status | Details |
|-------|--------|---------|
| `/login` | **Functional** | Email/password form, stores JWT on success, redirects to dashboard |
| `/register` | **Functional** | Email/password registration (min 8 chars), redirects to login |
| `/dashboard` | **Functional** | Protected — balance, income/expenses/net savings, budget progress, recent transactions, spending + income/expense charts, date range filter |
| `/transactions` | **Functional** | Protected — create/edit/delete, server-side search/filter/sort/pagination, category autocomplete, empty states |
| `/budgets` | **Functional** | Protected — add/edit/delete budgets, progress bars, loading/error states |

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
| GET | `/auth/me` | ✅ Working — returns authenticated user's safe profile (`id`, `email`, `created_at`) |
| GET | `/transactions` | ✅ Working — paginated list with search, type/category filters, sort; requires auth |
| GET | `/transactions/categories` | ✅ Working — distinct categories for current user (autocomplete) |
| POST | `/transactions` | ✅ Working — requires auth, normalizes category on save |
| PUT | `/transactions/{id}` | ✅ Working — requires auth, updates user's own transaction |
| DELETE | `/transactions/{id}` | ✅ Working — requires auth, deletes user's own transaction |
| GET | `/budgets` | ✅ Working — requires auth, returns current user's budgets |
| POST | `/budgets` | ✅ Working — requires auth, normalizes category on save |
| PUT | `/budgets/{id}` | ✅ Working — requires auth, updates user's own budget |
| DELETE | `/budgets/{id}` | ✅ Working — requires auth, deletes user's own budget |
| GET | `/budgets/progress` | ✅ Working — case-insensitive category matching for spent totals |
| GET | `/dashboard` | ✅ Working — aggregated overview; optional `?start_date=&end_date=` filters |

**Query parameters (M8):**

- `GET /transactions` — `page`, `page_size`, `sort_by` (`date` \| `amount` \| `category`), `sort_order` (`asc` \| `desc`), `search`, `type`, `category`
- `GET /dashboard` — `start_date` (YYYY-MM-DD), `end_date` (YYYY-MM-DD); omit both for default all-time/current-month behavior

**Transaction list response shape:**

```json
{
  "items": [...],
  "page": 1,
  "page_size": 25,
  "total_count": 42,
  "total_pages": 2
}
```

#### Authentication

- [x] Password hashing via passlib + bcrypt (`bcrypt==4.0.1` pinned for compatibility)
- [x] JWT creation and validation (`python-jose`)
- [x] `get_current_user` FastAPI dependency — reads `Authorization: Bearer <token>`
- [x] All data routes protected and scoped to authenticated user
- [x] Pydantic schemas: `UserCreate`, `LoginRequest`, `TokenResponse`, `UserResponse`, `TransactionUpdate`, `TransactionListResponse`, `DashboardResponse`

### Database

- [x] PostgreSQL connected from backend
- [x] `transactions` table with `user_id` FK → `users.id` ON DELETE CASCADE
- [x] `users` table with auth fields (`email`, `hashed_password`, `created_at`)
- [x] `budgets` table with `user_id` FK → `users.id` ON DELETE CASCADE
- [x] Startup migration adds missing auth columns and foreign keys to legacy databases

---

## What Is NOT Implemented

### Transactions (remaining polish)

- [ ] Transaction detail view (single-transaction page)

### General / Infrastructure

- [ ] Frontend Docker service in Compose
- [ ] Unit / integration tests
- [ ] CI/CD pipeline
- [ ] Production deployment config

### Future polish (deferred)

- [ ] Next.js middleware for server-side route protection
- [ ] Token refresh / rotation
- [ ] httpOnly cookie storage
- [ ] Alembic migrations
- [ ] Dedicated category database table
- [ ] Advanced dashboard analytics (goals, forecasts, etc.)

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
│   │   ├── dashboard/         ← widgets, charts, date range, skeleton
│   │   ├── layout/            ← sidebar + shell
│   │   ├── transactions/      ← form, list, filters, pagination, autocomplete, edit dialog
│   │   └── ui/                ← skeleton, error-state, shadcn primitives
│   └── lib/
│       ├── api.ts             ← backend HTTP client
│       ├── auth.ts            ← JWT storage and helpers
│       ├── categories.ts      ← common + merged user categories
│       ├── date-range.ts      ← dashboard date presets
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
        │   ├── auth.py        ← register, login, /me
        │   ├── budgets.py
        │   ├── dashboard.py   ← optional date range query params
        │   └── transactions.py ← pagination, sort, filters, /categories
        ├── services/
        │   ├── budget.py
        │   └── dashboard.py   ← income/expense comparison, date-scoped aggregation
        ├── db/migrate.py
        ├── models/
        └── schemas/
            ├── dashboard.py
            └── transaction_list.py
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

### Manual test checklist

1. Register a new account at `/register`
2. Sign in at `/login`
3. Create income and expense transactions on `/transactions`
4. Edit and delete transactions; verify category autocomplete suggestions
5. Use search, type/category filters, sorting, and pagination
6. Create budgets on `/budgets`; verify progress updates
7. Open `/dashboard` — verify balance, summary cards, charts
8. Change date range presets; confirm metrics and charts update
9. Sign in as a second user — confirm no access to the first user's data

---

## Suggested Next Steps (Milestone 9+)

1. **Deployment** — frontend Docker service, production Compose config, environment hardening
2. **CI/CD** — automated tests and deploy pipeline
3. **Auth hardening** — token refresh, httpOnly cookies, Next.js middleware
4. **Database migrations** — Alembic for schema versioning
5. **Category model** — dedicated table with managed categories (replace autocomplete-only approach)
