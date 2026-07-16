# Project Status

Living document tracking what has been built and what remains.

Last updated: July 15, 2026 (Natural Language Financial Actions — M19)

**Current state:** Production application live at **https://app.jakesfinancetracker.com** with API at **https://api.jakesfinancetracker.com**. Deployed on AWS ECS Fargate with RDS PostgreSQL, ALB HTTPS termination (ACM), and automated GitHub Actions CI/CD. All 19 milestones complete. Authentication uses httpOnly Secure cookies (no client-side JWT storage). Gemini-powered AI financial insights and natural language transaction/budget creation are available on the dashboard when enabled. Frontend supports responsive layouts for phones, tablets, and desktops.

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
| M15 — HTTPS deployment | Complete | Custom domains, ACM certificates, ALB TLS, HTTPS CI/CD verification |
| M16 — Mobile responsiveness | Complete | Responsive layouts, mobile navigation, touch-friendly forms, page-level QA across all routes |
| M17 — Authentication hardening | Complete | httpOnly Secure cookies, cookie-only backend auth, `/auth/me` session validation, backend logout |
| M18 — AI Financial Insights | Complete | Gemini integration, authenticated `/ai/insights`, dashboard AI card, Markdown-formatted responses |
| M19 — Natural Language Financial Actions | Complete | Gemini intent parsing, transaction/budget creation via existing services, dashboard AI actions card, validation pipeline |

---

## What Is Implemented

### Infrastructure

- Repository layout (`frontend/`, `backend/`, root config)
- Docker Compose: PostgreSQL 16, FastAPI backend, Next.js frontend (all with health checks)
- Environment config (`.env.example`, `.env.production.example`, `APP_ENV`, `CORS_ORIGINS`, `DATABASE_URL`, `SECRET_KEY`, `NEXT_PUBLIC_API_URL`, `ACCESS_TOKEN_COOKIE_NAME`, `COOKIE_DOMAIN`, `COOKIE_SECURE`, `COOKIE_SAMESITE`, `COOKIE_HTTPONLY`, `TEST_DATABASE_URL`, `AI_ENABLED`, `AI_PROVIDER`, `AI_MODEL`, `GEMINI_API_KEY`)
- HTTPS-ready configuration: production URLs require `https://`; local development uses HTTP
- CORS credentialed requests enabled (`allow_credentials=True`) for cookie-based authentication
- Cookie helpers for JWT issuance and logout (`backend/app/core/cookies.py`)
- Production Dockerfiles with health checks and startup validation
- Production startup skips automatic schema changes (`APP_ENV=production`)
- Startup validation for required config and database connectivity
- Structured logging on backend startup and shutdown
- GitHub Actions CI (`.github/workflows/ci.yml`) on push/PR to `main`
- GitHub Actions CD (`.github/workflows/deploy.yml`) on push to `main` after CI passes
- AWS production deployment (ECS Fargate, ALB, RDS PostgreSQL, ECR, ACM, Route 53)
- Production HTTPS: https://app.jakesfinancetracker.com / https://api.jakesfinancetracker.com

### Frontend

- Next.js 15 (App Router, TypeScript, Tailwind CSS v4)
- shadcn/ui, React Hook Form + Zod, Lucide React, Recharts
- Off-white / soft-green theme; Geist Sans via `next/font`
- Full-height sidebar app shell at `lg` (1024px+); hamburger menu with slide-out drawer below `lg`
- Authenticated routes behind `AuthGuard` (validates session via `GET /auth/me`)
- Responsive page layouts with scaled spacing (`space-y-5` mobile → `lg:space-y-8` desktop)
- Login and registration pages; JWT stored in httpOnly Secure cookies (not accessible to JavaScript)
- API client uses `credentials: "include"` on all requests; no `Authorization` headers
- Loading skeletons and error states with retry
- Health endpoint: `GET /health` (public, no auth; used by ALB target group)
- Custom 404 page (`app/not-found.tsx`) matching app design system
- Shared `DialogShell` for scrollable edit dialogs on small screens
- `useMediaQuery` hook for responsive chart sizing
- `AIInsightsCard` dashboard component with Gemini-powered financial insights
- `AIActionsCard` dashboard component for natural language transaction and budget creation
- Markdown rendering for AI responses (`react-markdown`)
- AI loading, success, disabled, and error states with refresh/retry
- AI action loading skeleton, success confirmation, duplicate-request guard, and clearer error mapping
- Dashboard silent refresh after successful AI actions (recent transactions, budgets, summary cards)
- AI requests use existing `authFetch()` with `credentials: "include"`

#### Pages

| Route | Status | Details |
|-------|--------|---------|
| `/login` | Functional | Email/password form; backend sets httpOnly cookie; redirects to dashboard; responsive layout |
| `/register` | Functional | Email/password registration (min 8 chars), redirects to login; responsive layout |
| `/dashboard` | Functional | All-time balance; current-month income/expenses; top 5 budgets by usage; 5 recent transactions; charts; AI insights and AI actions cards; responsive grids and charts |
| `/transactions` | Functional | Create/edit/delete with user-selected date; free-text category; search, type/category filters, pagination; card layout below `lg`, table at `lg+` |
| `/budgets` | Functional | Add/edit/delete budgets, progress bars, loading/error states; responsive card grid |
| `/health` | Functional | Public health check; returns `{"status":"ok"}` for ALB |
| `/*` (unknown routes) | Functional | Custom 404 page via `app/not-found.tsx`; responsive centered layout |

### Backend

- FastAPI with CORS, SQLAlchemy 2.x, Pydantic schemas
- Health endpoint: `GET /health`
- Password hashing (passlib + bcrypt), JWT auth via httpOnly cookies (`python-jose`)
- `POST /auth/logout` clears authentication cookie
- All data routes protected and scoped to authenticated user
- Category normalization (trim + title case); case-insensitive budget matching
- Lightweight startup migrations for legacy databases
- pytest suite with isolated `finance_app_test` database
- Gemini AI service layer (`backend/app/services/ai_service.py`)
- AI insights service with user-scoped financial context (`backend/app/services/ai_insights_service.py`)
- AI action service with intent parsing and validation (`backend/app/services/ai_action_service.py`)
- Shared domain helpers: `create_transaction_for_user()`, `create_budget_for_user()`
- AI schemas (`backend/app/schemas/ai.py`)
- `POST /ai/insights` authenticated API endpoint
- `POST /ai/action` authenticated natural language action endpoint
- AI tests with mocked Gemini responses (`backend/tests/test_ai.py`)

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
| POST | `/auth/login` | Sets httpOnly cookie; returns user info |
| POST | `/auth/logout` | Clears authentication cookie |
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
| POST | `/ai/insights` | Gemini-powered financial insights for authenticated user |
| POST | `/ai/action` | Natural language transaction/budget creation for authenticated user |

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

### Mobile responsiveness (M16)

Responsive layout foundation across all frontend pages. Desktop appearance at `lg` (1024px+) is preserved; phones and tablets receive adapted layouts.

| Area | Implementation |
|------|----------------|
| Mobile navigation | Hamburger menu and slide-out drawer below `lg`; permanent sidebar unchanged at `lg+` |
| Responsive layouts | `min-w-0` and `overflow-x-hidden` containment; scaled page padding and section spacing |
| Responsive forms | Full-width inputs on small screens; stacked submit/cancel buttons; `h-10` touch targets on mobile |
| Responsive dashboard | Stacked summary cards on mobile; responsive chart heights and compact axis/legend sizing |
| Responsive transactions | Wrapping filter controls; card-based transaction list below `lg`; table view at `lg+` |
| Responsive budgets | Single-column card grid on mobile; responsive progress bars and edit dialogs |
| Tablet support | Intermediate breakpoints (`sm`, `md`) for grids, spacing, and two-column form layouts |
| Touch usability | Larger icon buttons in navigation and action rows; full-width pagination buttons on mobile |

**Mobile navigation**
- `AppShell` shows a mobile header with hamburger button below `lg`
- Slide-out drawer reuses `SidebarNavContent` with close button and route-change auto-close
- Desktop sidebar (`w-64`, full viewport height) unchanged at `lg+`

**Responsive layouts**
- Page content padding: `px-4 py-6` mobile → `sm:px-6 sm:py-8` → `lg:px-8 lg:py-8` desktop
- Section spacing: `space-y-5` mobile → `sm:space-y-6` → `lg:space-y-8` desktop
- Grid children use `[&>*]:min-w-0` to prevent card overflow

**Responsive forms**
- Create/edit forms on transactions and budgets: single-column on mobile, two-column at `sm+`
- Select triggers default to `w-full min-w-0`
- Edit dialogs use `DialogShell` with `max-h-[calc(100dvh-2rem)]` and vertical scroll

**Responsive dashboard**
- Summary cards stack vertically on mobile; `sm:grid-cols-2`, `lg:grid-cols-3` on larger screens
- Charts use `ResponsiveContainer` with scaled heights and compact tick/legend sizing below `lg`
- Budget progress and recent transaction widgets wrap content and truncate long text

**Responsive transactions**
- Filter row stacks on mobile; search spans full width
- Transaction list renders stacked cards below `lg`; existing table preserved at `lg+`
- Pagination buttons full-width on mobile in a two-column grid

**Responsive budgets**
- Budget cards in responsive grid (`grid-cols-1` → `sm:grid-cols-2` → `lg:grid-cols-3`)
- Progress bars use `overflow-hidden` tracks; category and amount rows wrap on narrow screens
- Create and edit budget dialogs match transaction dialog responsive patterns

**Authentication and 404**
- Login and register pages: centered layout, `max-w-md`, responsive typography and touch-friendly inputs/buttons
- 404 page: scaled heading (`text-6xl` → `lg:text-8xl`), stacked full-width action buttons on mobile

**QA pass**
- Full responsive review across all pages at 320–1440px widths
- Horizontal scrolling, clipped dialogs/charts, and inconsistent breakpoints addressed
- Frontend build verified after changes

### HTTPS deployment (M15)

Production HTTPS is fully configured and verified.

| Item | Status |
|------|--------|
| Custom domain — frontend (`app.jakesfinancetracker.com`) | Complete |
| Custom domain — backend (`api.jakesfinancetracker.com`) | Complete |
| ACM SSL/TLS certificates | Complete |
| ALB HTTPS listeners (port 443) | Complete |
| HTTP → HTTPS redirect | Complete |
| DNS routing to ALBs | Complete |
| Production env vars use `https://` URLs | Complete |
| CD pipeline verifies HTTPS health endpoints | Complete |
| End-to-end HTTPS deployment | Verified |

Production URLs:

- Frontend: https://app.jakesfinancetracker.com
- Backend API: https://api.jakesfinancetracker.com
- Health check: https://api.jakesfinancetracker.com/health

### Automated tests (M10)

| Module | Coverage |
|--------|----------|
| `test_auth.py` | Registration, login, cookie auth, logout, password hashing, protected routes |
| `test_transactions.py` | CRUD, category normalization, user isolation |
| `test_budgets.py` | CRUD, case-insensitive progress |
| `test_dashboard.py` | Balance aggregation, monthly filtering, widget limits |
| `test_ai.py` | AI disabled fallback, insights generation, action parsing/validation/execution, mocked Gemini, error mapping |

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
- Frontend image built with `NEXT_PUBLIC_API_URL=https://api.jakesfinancetracker.com`
- Health checks: backend and frontend `GET /health` (ALB target groups)

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
- HTTPS health checks verified on both frontend and backend
- Live at https://app.jakesfinancetracker.com

See [README.md](./README.md#continuous-integration) and [README.md](./README.md#continuous-deployment) for details.

### Authentication hardening (M17)

Production authentication uses httpOnly Secure cookies instead of client-side JWT storage.

| Area | Implementation |
|------|----------------|
| Login | Backend validates credentials, creates JWT, sets `access_token` httpOnly cookie |
| Session validation | `AuthGuard` and sidebar call `GET /auth/me` with `credentials: "include"` |
| API requests | Browser sends cookie automatically; no `Authorization: Bearer` header |
| Logout | `POST /auth/logout` clears cookie; frontend redirects to `/login` |
| Backend auth | `get_current_user()` reads JWT exclusively from cookie |
| Cross-subdomain | Production `COOKIE_DOMAIN=.jakesfinancetracker.com` for `app.*` → `api.*` |
| Cookie flags | `COOKIE_SECURE`, `COOKIE_SAMESITE`, `COOKIE_HTTPONLY` env-driven |

### AI Financial Insights (M18)

Integrated a Gemini-powered AI financial assistant that generates personalized financial insights from user-scoped transaction and budget data.

**Status:** Complete

**Summary:** The backend aggregates each user's financial data into a sanitized context, sends it to Gemini, and returns Markdown-formatted insights. The dashboard displays the response with proper formatting. The Gemini API key never leaves the backend.

**Implemented:**
- Backend Gemini API integration (`google-genai`)
- Configurable AI provider/model settings (`AI_PROVIDER`, `AI_MODEL`)
- Authenticated `POST /ai/insights` endpoint
- User-specific financial context generation (income, expenses, categories, budgets, trends)
- Dashboard `AIInsightsCard` component
- Markdown-formatted AI responses (`react-markdown` on frontend)
- Backend-only API key handling
- AI disabled fallback behavior when `AI_ENABLED=false`
- Error handling for AI failures (rate limits, provider errors, empty responses)

**Frontend:**
- Dashboard contains `AIInsightsCard` (`frontend/components/dashboard/ai-insights-card.tsx`)
- Uses existing cookie authentication — no separate AI auth flow
- Calls backend `POST /ai/insights` via `getAIInsights()` in `lib/api.ts`
- Displays loading, success, disabled, and error states
- Refresh button with duplicate-request guard
- Renders bold headings, bullet lists, and paragraphs from Markdown

**Backend:**
- `POST /ai/insights` requires authentication (`get_current_user`)
- Uses only the authenticated user's transaction and budget data
- Builds sanitized financial context in `ai_insights_service.py`
- Sends aggregated financial information to Gemini — not raw database rows
- Does **not** send:
  - user email
  - user ID
  - transaction descriptions
  - private identifying information

**AI configuration (environment variables):**

| Variable | Purpose |
|----------|---------|
| `AI_ENABLED` | Master switch — when `false`, endpoint returns disabled message without calling Gemini |
| `AI_PROVIDER` | Provider identifier (currently `gemini`) |
| `AI_MODEL` | Gemini model name (e.g. `gemini-2.0-flash`) |
| `GEMINI_API_KEY` | Google Gemini API key — **backend only** |

**Security notes:**
- `GEMINI_API_KEY` is backend-only and never exposed to the frontend
- The frontend has no AI API keys or direct Gemini access
- Production configuration is stored through ECS task definition environment variables (or secrets)
- Tests force `AI_ENABLED=false` in `conftest.py` to avoid real API calls

### Natural Language Financial Actions (M19)

Users can create transactions and budgets from plain English on the dashboard. The AI interprets intent; existing CRUD services perform all database writes.

**Status:** Complete

**Summary:** The backend sends the user's message to Gemini with a structured prompt (reference date, relative date rules, merchant/category mapping, income vs expense wording). Gemini returns JSON; the backend validates and executes supported intents via `create_transaction_for_user()` and `create_budget_for_user()`. The AI never writes directly to the database.

**Supported examples:**
- "I spent $42 at Costco"
- "I got paid $1800"
- "Make a $250 grocery budget"
- "I paid $65 for gas yesterday"
- "I bought lunch for $17"

**Frontend (`AIActionsCard`):**
- Textarea for natural language input; submit button with loading state
- Loading skeleton and pulse animation while Gemini parses the message
- Duplicate-request protection (ignores repeat submits while in flight)
- Success state with created transaction or budget details (`CheckCircle2`)
- Clear error messages for parse errors, validation errors, rate limits, and auth expiry
- `onActionSuccess` callback triggers silent dashboard refresh (recent transactions, budget overview, summary cards)

**Backend pipeline:**
1. `POST /ai/action` — authenticated; receives `{ "message": "..." }`
2. Empty message → `validation_error` (no Gemini call)
3. `build_action_prompt()` — reference date, relative dates (today, yesterday, last Friday, this morning, last week), merchant/category hints, example phrases
4. `generate_text()` — Gemini returns JSON only
5. `parse_action_json()` — Pydantic models (`CreateTransactionAction`, `CreateBudgetAction`, `UnknownAction`)
6. `validate_transaction_action()` / `validate_budget_action()` — reject ambiguous/generic descriptions
7. `resolve_action_date()` — `today`, `yesterday`, or ISO `YYYY-MM-DD`
8. `execute_parsed_action()` — delegates to domain services with `TransactionCreate` / `BudgetCreate` schemas (same validation as manual CRUD)
9. Unknown or unsupported intents → `validation_error` with user-facing reason (no DB write)

**Security:**
- `GEMINI_API_KEY` remains backend-only; only the user's message is sent to Gemini (no financial aggregates, emails, or IDs)
- AI output is validated before any write; malformed JSON and ambiguous intents never reach the database
- All creates are scoped to the authenticated user via existing service functions

---

## What Is NOT Implemented

- Transaction detail view (single-transaction page)
- Category autocomplete (intentionally removed; free-text only)
- Alembic migrations (production schema changes are manual when `APP_ENV=production`)
- Next.js middleware for server-side route protection
- Token refresh / rotation
- Dedicated category database table
- Advanced dashboard analytics (goals, forecasts, etc.)
- Dashboard date range selector UI (removed; backend params remain)

**Future AI features (not yet built):**
- AI chat assistant with conversation history
- Stored AI conversations
- AI memory / personalization beyond per-request context
- Auto-refresh on `/transactions` and `/budgets` pages after AI actions (dashboard refreshes today)

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
│   ├── components/             auth, budgets, dashboard (AIInsightsCard, AIActionsCard), layout, transactions, ui
│   ├── hooks/                  use-media-query
│   └── lib/                    api, auth, format, parse-insights, types
├── backend/
│   ├── Dockerfile
│   ├── pytest.ini
│   ├── requirements-dev.txt
│   ├── tests/                  conftest + auth/transactions/budgets/dashboard/ai tests (66 tests)
│   └── app/
│       ├── main.py
│       ├── core/               config, auth, categories, cookies
│       ├── api/routes/         auth, ai, budgets, dashboard, transactions
│       ├── services/           ai, ai_action, ai_insights, budget, dashboard, transaction
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
5. Open `/dashboard` — summary cards, top 5 budgets, 5 recent transactions, charts, AI insights and AI actions (if enabled)
6. On dashboard AI actions card, try "I spent $42 at Costco" — confirm transaction appears in recent transactions after success
7. Confirm sidebar spans full viewport height at `lg+`; hamburger navigation works below `lg`
8. Sign in as a second user — confirm data isolation
9. Resize browser to 320px, 768px, and 1440px — confirm no horizontal scrolling on dashboard, transactions, budgets, login, and 404
10. Try an ambiguous AI action (e.g. "spent money") — confirm validation error, no new transaction

---

## Suggested Next Steps

1. Alembic migrations — replace manual production schema provisioning
2. CD hardening — GitHub OIDC instead of long-lived AWS access keys; deployment approval gates
3. Token refresh and Next.js middleware — optional auth enhancements
