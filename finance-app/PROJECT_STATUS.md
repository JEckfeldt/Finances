# Project Status

Living document tracking what has been built and what remains.

Last updated: July 2026

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

---

## What Is Implemented

### Infrastructure

- Monorepo layout (`frontend/`, `backend/`, root config)
- Docker Compose: PostgreSQL 16 (persistent volume, health check)
- Docker Compose: FastAPI backend service
- Environment config (`.env.example`, `CORS_ORIGINS`, `DATABASE_URL`, `SECRET_KEY`, `NEXT_PUBLIC_API_URL`)
- Root `.gitignore`

### Frontend

- Next.js 15 (App Router, TypeScript, Tailwind CSS v4)
- shadcn/ui (base-nova style): Button, Card, Input, Label, Select, Table, Badge, Separator, Skeleton
- React Hook Form + Zod (transactions and budgets forms)
- Lucide React icons
- Recharts (spending trends chart, income vs expense comparison chart)
- Off-white / soft-green theme in `globals.css`
- Global typography: Geist Sans via `next/font`, wired through Tailwind `font-sans`
- App shell with full-height sidebar (`h-screen` layout, `AppShell`, `SidebarNav`)
- Route group `(main)` wrapping authenticated pages behind `AuthGuard`
- Root `/` redirects to `/dashboard`
- API client (`lib/api.ts`) and shared types (`lib/types.ts`)
- Auth state management (`lib/auth.ts`): JWT + email in `localStorage`
- Login and registration pages (`/login`, `/register`)
- Sidebar logout button; email from `/auth/me` (synced to localStorage)
- Loading skeletons and error states with retry (`components/ui/skeleton.tsx`, `error-state.tsx`)

#### Pages

| Route | Status | Details |
|-------|--------|---------|
| `/login` | Functional | Email/password form, stores JWT on success, redirects to dashboard |
| `/register` | Functional | Email/password registration (min 8 chars), redirects to login |
| `/dashboard` | Functional | Balance, income, and expense summary cards; budget progress; recent transactions; spending and income/expense charts |
| `/transactions` | Functional | Create/edit/delete with user-selected transaction date; free-text category; server-side search, type/category filters, pagination; empty states |
| `/budgets` | Functional | Add/edit/delete budgets, progress bars, loading/error states |

### Backend

- FastAPI app with CORS middleware
- Health endpoint: `GET /health`
- SQLAlchemy 2.x engine + session (`db/session.py`, `db/base.py`)
- Config from environment (`core/config.py`): `SECRET_KEY`, `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`
- Auto table creation on startup (`Base.metadata.create_all`)
- Lightweight startup migrations (`db/migrate.py`): users columns, transaction_date column, foreign keys
- Package structure: `api/`, `core/`, `models/`, `schemas/`, `services/`, `db/`
- Business logic in `services/`: budget progress and dashboard aggregation
- Category normalization (`core/categories.py`): trim + title case on save, case-insensitive budget matching

#### Models

| Model | Status | Fields |
|-------|--------|--------|
| `Transaction` | Active | `id`, `user_id` (FK, CASCADE), `description`, `amount`, `type`, `category`, `transaction_date`, `created_at` |
| `User` | Active | `id`, `email` (unique, indexed), `hashed_password`, `created_at` |
| `Budget` | Active | `id`, `user_id` (FK, CASCADE), `category`, `limit_amount`, `created_at`, `updated_at` |

Field notes:

- `transaction_date`: user-selected date of the financial event
- `created_at`: record creation timestamp (unchanged)

#### API Endpoints

| Method | Endpoint | Status |
|--------|----------|--------|
| GET | `/health` | Working |
| POST | `/auth/register` | Working — creates user, returns safe user info |
| POST | `/auth/login` | Working — returns JWT `{ access_token, token_type: "bearer" }` |
| GET | `/auth/me` | Working — returns `id`, `email`, `created_at` |
| GET | `/transactions` | Working — paginated list with search, type/category filters, sort; requires auth |
| GET | `/transactions/categories` | Working — distinct categories for filter dropdown |
| POST | `/transactions` | Working — requires auth, normalizes category on save |
| PUT | `/transactions/{id}` | Working — requires auth, updates user's own transaction |
| DELETE | `/transactions/{id}` | Working — requires auth, deletes user's own transaction |
| GET | `/budgets` | Working — requires auth |
| POST | `/budgets` | Working — requires auth |
| PUT | `/budgets/{id}` | Working — requires auth |
| DELETE | `/budgets/{id}` | Working — requires auth |
| GET | `/budgets/progress` | Working — case-insensitive category matching |
| GET | `/dashboard` | Working — aggregated overview; optional `start_date` / `end_date` query params (backend only; frontend uses defaults) |

Query parameters:

- `GET /transactions` — `page`, `page_size`, `sort_by` (`date` | `amount` | `category`), `sort_order` (`asc` | `desc`), `search`, `type`, `category`
- `GET /dashboard` — `start_date` (YYYY-MM-DD), `end_date` (YYYY-MM-DD); optional, not used by current frontend

Transaction list response shape:

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

- Password hashing via passlib + bcrypt (`bcrypt==4.0.1` pinned)
- JWT creation and validation (`python-jose`)
- `get_current_user` FastAPI dependency
- All data routes protected and scoped to authenticated user

### Database

- PostgreSQL connected from backend
- `transactions` table with `user_id` FK to `users.id` ON DELETE CASCADE
- `users` table with auth fields
- `budgets` table with `user_id` FK to `users.id` ON DELETE CASCADE
- Startup migrations add missing columns and foreign keys for legacy databases

---

## Post-M8 Changes

Changes applied after Milestone 8 without starting Milestone 9:

| Change | Details |
|--------|---------|
| Net Savings card removed | Dashboard summary shows Balance, Income, and Expenses only (3-column grid) |
| Full-height sidebar | App shell uses `h-screen` so sidebar spans the viewport |
| Global typography fix | Geist Sans wired via `layout.tsx` and `globals.css` |
| Category input simplified | Free-text category on create/edit; filter dropdown on list view retained |
| Sort controls removed (UI) | Transactions page no longer shows Sort By / Order; list defaults to date descending via API |
| Transaction date field | User-selectable `transaction_date` on create/edit; displayed in list and dashboard recent transactions |
| Dashboard date selector removed (UI) | Date range dropdown removed from dashboard; default metrics always shown |

---

## What Is NOT Implemented

### Transactions

- Transaction detail view (single-transaction page)
- Category autocomplete on create/edit forms (intentionally removed; free-text only)

### General / Infrastructure

- Frontend Docker service in Compose
- Unit / integration tests
- CI/CD pipeline
- Production deployment config

### Future polish (deferred)

- Next.js middleware for server-side route protection
- Token refresh / rotation
- httpOnly cookie storage
- Alembic migrations
- Dedicated category database table
- Advanced dashboard analytics (goals, forecasts, etc.)
- Dashboard date range selector UI (removed; backend params remain)

---

## Key Files Reference

```
finance-app/
├── PROJECT_STATUS.md
├── README.md
├── docker-compose.yml
├── .env.example
│
├── frontend/
│   ├── app/
│   │   ├── layout.tsx              Geist font loading, global typography
│   │   ├── globals.css             Theme tokens, font-sans wiring
│   │   ├── (main)/
│   │   │   ├── layout.tsx          AuthGuard + AppShell wrapper
│   │   │   ├── dashboard/page.tsx
│   │   │   ├── transactions/page.tsx
│   │   │   └── budgets/page.tsx
│   │   ├── login/page.tsx
│   │   └── register/page.tsx
│   ├── components/
│   │   ├── auth/auth-guard.tsx
│   │   ├── budgets/                Form, card, edit dialog
│   │   ├── dashboard/              Widgets, charts, skeleton
│   │   ├── layout/                 Full-height sidebar + shell
│   │   ├── transactions/           Form, list, filters, pagination, edit dialog
│   │   └── ui/                     Skeleton, error-state, shadcn primitives
│   └── lib/
│       ├── api.ts
│       ├── auth.ts
│       ├── format.ts               Currency and date formatting
│       └── types.ts
│
└── backend/
    ├── Dockerfile
    └── app/
        ├── main.py
        ├── core/                     config, auth, categories
        ├── api/routes/               auth, budgets, dashboard, transactions
        ├── services/                 budget.py, dashboard.py
        ├── db/migrate.py
        ├── models/
        └── schemas/
```

---

## How to Run

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
3. Create transactions with a custom transaction date and free-text category
4. Edit and delete transactions; confirm date is preserved/updated
5. Use search, type/category filters, and pagination on `/transactions`
6. Create budgets on `/budgets`; verify progress updates
7. Open `/dashboard` — verify summary cards, budget progress, recent transactions, and charts
8. Confirm sidebar spans full viewport height on short pages
9. Sign in as a second user — confirm no access to the first user's data

---

## Suggested Next Steps (Milestone 9+)

1. Deployment — frontend Docker service, production Compose config, environment hardening
2. CI/CD — automated tests and deploy pipeline
3. Auth hardening — token refresh, httpOnly cookies, Next.js middleware
4. Database migrations — Alembic for schema versioning
5. Category model — dedicated table with managed categories (optional; forms currently use free-text input)
