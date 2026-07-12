# Jake's Finance Tracker

![CI](https://github.com/JEckfeldt/Finances/actions/workflows/ci.yml/badge.svg)

A full-stack personal finance application for tracking transactions, managing budgets, and viewing financial analytics. Built with Next.js and FastAPI, containerized with Docker, and deployed to AWS ECS Fargate with automated CI/CD.

**Live Demo:** [https://app.jakesfinancetracker.com](https://app.jakesfinancetracker.com)  
**API:** [https://api.jakesfinancetracker.com](https://api.jakesfinancetracker.com)  
**API Health:** [https://api.jakesfinancetracker.com/health](https://api.jakesfinancetracker.com/health)

> See [PROJECT_STATUS.md](./PROJECT_STATUS.md) for milestone history and implementation details.

---

## Features

- User registration and JWT authentication with per-user data isolation
- Transaction management — create, edit, delete, search, filter, and paginate
- Budget tracking with progress bars and case-insensitive category matching
- Financial dashboard — balance, monthly income/expenses, spending charts, recent transactions
- Custom 404 page and `/health` endpoints for production monitoring
- Responsive layouts for phones, tablets, and desktops (hamburger navigation below `lg`, responsive forms and page grids)
- Automated testing, Docker-based deployment, and GitHub Actions CI/CD

---

## Tech Stack

**Frontend**
- Next.js 15, TypeScript, Tailwind CSS v4
- shadcn/ui, React Hook Form, Zod, Lucide React, Recharts
- Responsive layouts with mobile hamburger navigation (desktop sidebar at `lg` / 1024px+)

**Backend**
- FastAPI, SQLAlchemy 2.x, Pydantic, python-jose, passlib, psycopg

**Database**
- PostgreSQL 16

**Infrastructure**
- Docker, Docker Compose, Amazon ECS Fargate, ECR, RDS, ALB, ACM
- GitHub Actions (CI + CD)

---

## Architecture

```
Browser
   |
   v
Application Load Balancer (HTTPS / ACM)
   |
   +-- Frontend (ECS Fargate) — Next.js on port 3000
   |
   +-- Backend (ECS Fargate) — FastAPI on port 8000
           |
           v
       Amazon RDS (PostgreSQL 16)
```

**Production URLs**

| Service | URL |
|---------|-----|
| Frontend | https://app.jakesfinancetracker.com |
| Backend API | https://api.jakesfinancetracker.com |
| API docs | https://api.jakesfinancetracker.com/docs |
| Health check | https://api.jakesfinancetracker.com/health |

**Repository layout**

```
/
├── frontend/              Next.js application
├── backend/               FastAPI application
│   └── tests/             pytest suite
├── docker-compose.yml     Local development stack
├── .env.example           Development environment template
├── .env.production.example
└── .github/workflows/     CI and CD pipelines
```

---

## Local Development

### Prerequisites

- Docker and Docker Compose (recommended)
- Node.js 20+ (optional, for frontend-only dev)
- Python 3.12+ (optional, for backend-only dev)

### Quick start (Docker)

```bash
cp .env.example .env
docker compose up -d --build
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API docs | http://localhost:8000/docs |

Stop services: `docker compose down` (add `-v` to remove database data).

### Frontend only

```bash
docker compose up -d postgres backend
cd frontend
npm install
cp ../.env.example .env.local
npm run dev
```

### Backend only

```bash
docker compose up -d postgres
cd backend
python -m venv .venv
source .venv/bin/activate          # macOS/Linux
# .venv\Scripts\Activate.ps1       # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Environment variables

| Variable | Description |
|----------|-------------|
| `APP_ENV` | `development` or `production` |
| `DATABASE_URL` | PostgreSQL connection string |
| `SECRET_KEY` | JWT signing key (32+ chars in production) |
| `CORS_ORIGINS` | Allowed frontend origins (`http://` locally, `https://` in production) |
| `NEXT_PUBLIC_API_URL` | Backend URL for frontend (build-time in Docker) |
| `COOKIE_SECURE` | `false` locally, `true` in production |
| `COOKIE_SAMESITE` | Cookie SameSite policy (`lax`, `strict`, `none`) |
| `TEST_DATABASE_URL` | Optional isolated test database |

See [`.env.example`](.env.example) for development and [`.env.production.example`](.env.production.example) for production.

### Backend testing

Requires PostgreSQL running (`docker compose up -d postgres`).

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # macOS/Linux
pip install -r requirements-dev.txt
pytest
```

24 integration tests cover auth, transactions, budgets, and dashboard endpoints. Tests use an isolated `finance_app_test` database.

### Reproduce CI checks locally

```bash
# Backend tests
cd backend && source .venv/bin/activate
export APP_ENV=development SECRET_KEY=ci-secret-key-with-at-least-32-characters
export CORS_ORIGINS=http://localhost:3000
export TEST_DATABASE_URL=postgresql+psycopg://finance_user:finance_pass@localhost:5432/finance_app_test
export DATABASE_URL=$TEST_DATABASE_URL
pytest

# Frontend build
cd frontend && npm ci && npm run lint --if-present
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run build

# Docker validation
docker build -t finance-backend:local ./backend
docker build --build-arg NEXT_PUBLIC_API_URL=http://localhost:8000 -t finance-frontend:local ./frontend
docker compose config --quiet
```

---

## Production Deployment

The application is live on AWS with HTTPS, custom domains, and automated deployments.

**Current production**

- Frontend: https://app.jakesfinancetracker.com
- Backend: https://api.jakesfinancetracker.com
- TLS terminated at ALB using ACM certificates
- HTTP redirects to HTTPS
- ECS Fargate services behind separate ALBs
- RDS PostgreSQL for persistent storage
- Docker images stored in ECR

### AWS resources

| Resource | Purpose |
|----------|---------|
| ECS Fargate (2 services) | Run frontend and backend containers |
| Application Load Balancer (2) | HTTPS termination and routing |
| Amazon RDS (PostgreSQL 16) | Application database |
| Amazon ECR (2 repositories) | Docker image storage |
| ACM | SSL/TLS certificates |
| Route 53 / DNS | Custom domain routing |

### Production environment variables

| Variable | Service | Value |
|----------|---------|-------|
| `APP_ENV` | Backend | `production` |
| `DATABASE_URL` | Backend | RDS connection string |
| `SECRET_KEY` | Backend | Strong random 32+ char secret |
| `CORS_ORIGINS` | Backend | `https://app.jakesfinancetracker.com` |
| `NEXT_PUBLIC_API_URL` | Frontend build | `https://api.jakesfinancetracker.com` |
| `COOKIE_SECURE` | Backend | `true` |
| `COOKIE_SAMESITE` | Backend | `lax` |

Backend validates config on startup, verifies database connectivity, and exposes `GET /health` (no auth required). Frontend image must be built with `NEXT_PUBLIC_API_URL` set at build time:

```bash
docker build --build-arg NEXT_PUBLIC_API_URL=https://api.jakesfinancetracker.com -t finance-frontend ./frontend
```

### HTTPS configuration (completed)

1. Custom domains configured (`app.jakesfinancetracker.com`, `api.jakesfinancetracker.com`)
2. ACM SSL/TLS certificates issued and validated
3. HTTPS listeners (port 443) on both ALBs with ACM certificates attached
4. HTTP (port 80) listeners redirect to HTTPS
5. DNS points domains to ALBs
6. ECS environment variables use `https://` URLs
7. ALB health checks use `/health` on both services
8. End-to-end HTTPS deployment verified

### Common production issues

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Backend exits on startup | Invalid `DATABASE_URL` or RDS unreachable | Check security groups and credentials |
| Frontend API calls fail | Wrong `NEXT_PUBLIC_API_URL` at build time | Rebuild frontend with correct HTTPS backend URL |
| CORS errors | `CORS_ORIGINS` mismatch | Set exact `https://` frontend origin |
| Health check failures | Wrong health check path | Ensure ALB checks `/health` |

---

## CI/CD Pipeline

Pushing to `main` triggers automated validation and production deployment.

```
git push main → CI (tests, build, Docker) → CD (ECR push, ECS deploy) → health verification
```

### CI — `.github/workflows/ci.yml`

Runs on every push and pull request to `main`:

| Job | Validates |
|-----|-----------|
| Backend Tests | pytest against PostgreSQL (Python 3.12) |
| Frontend Build | `npm ci`, ESLint, production build (Node 20) |
| Docker Validation | Image builds and `docker compose config` |

### CD — `.github/workflows/deploy.yml`

Runs after CI succeeds on `main`, or manually via **Actions → Deploy → Run workflow**:

1. Build backend and frontend Docker images (tagged with commit SHA)
2. Push images to Amazon ECR
3. Update ECS task definitions and deploy services
4. Wait for service stability
5. Verify backend `/health` and frontend availability

### GitHub configuration

**Secrets** (Settings → Secrets and variables → Actions → Secrets):

| Secret | Description |
|--------|-------------|
| `AWS_ACCESS_KEY_ID` | IAM deployment access key |
| `AWS_SECRET_ACCESS_KEY` | IAM deployment secret key |

**Variables** (Settings → Secrets and variables → Actions → Variables):

| Variable | Production value |
|----------|------------------|
| `AWS_REGION` | Your AWS region |
| `ECR_BACKEND_REPOSITORY` | Backend ECR repo name |
| `ECR_FRONTEND_REPOSITORY` | Frontend ECR repo name |
| `ECS_CLUSTER` | ECS cluster name |
| `ECS_BACKEND_SERVICE` | Backend service name |
| `ECS_FRONTEND_SERVICE` | Frontend service name |
| `ECS_BACKEND_CONTAINER_NAME` | Backend container name |
| `ECS_FRONTEND_CONTAINER_NAME` | Frontend container name |
| `NEXT_PUBLIC_API_URL` | `https://api.jakesfinancetracker.com` |
| `BACKEND_HEALTH_URL` | `https://api.jakesfinancetracker.com/health` |
| `FRONTEND_URL` | `https://app.jakesfinancetracker.com` |

### IAM permissions (minimum)

- **ECR:** push and pull images
- **ECS:** describe services/task definitions, register task definitions, update services
- **STS:** `GetCallerIdentity`

### Troubleshooting deployments

```bash
aws ecs describe-services \
  --cluster YOUR_CLUSTER \
  --services YOUR_SERVICE \
  --query 'services[0].events[:5]'
```

Check CloudWatch Logs for failed task output. To retry without a new commit: **Actions → Deploy → Run workflow**.

---

## Authentication notes

JWT tokens are currently stored in `localStorage` and sent via `Authorization: Bearer` headers. The codebase is prepared for future httpOnly Secure cookie migration (`credentials: "include"`, `COOKIE_SECURE`, `COOKIE_SAMESITE` env vars). Token refresh is not yet implemented.
