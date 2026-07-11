# Finance App

![CI](https://github.com/JEckfeldt/Finances/actions/workflows/ci.yml/badge.svg)

A personal finance management platform with a clean, modern dashboard aesthetic. Users can view their financial overview, manage transactions, and track budgets.

> **Project state:** See [PROJECT_STATUS.md](./PROJECT_STATUS.md) for a full breakdown of what is and is not implemented.

## Technology Stack

| Layer    | Technologies |
|----------|--------------|
| Frontend | Next.js 15, TypeScript, Tailwind CSS, shadcn/ui, React Hook Form, Zod, Lucide React, Recharts |
| Backend  | FastAPI, Uvicorn, SQLAlchemy 2.x, Pydantic, python-jose, passlib, psycopg |
| Database | PostgreSQL 16 |

## Prerequisites

- [Docker](https://www.docker.com/) and Docker Compose (recommended)
- [Node.js](https://nodejs.org/) 20+ (optional, for local frontend development)
- [Python](https://www.python.org/) 3.12+ (optional, for local backend development)

## Environment Setup

1. Clone the repository and navigate to the project root.

2. Copy the environment template:

   ```bash
   cp .env.example .env
   ```

3. Review `.env` and update values as needed. Do not commit real secrets.

### Environment Variables

| Variable | Description |
|----------|-------------|
| `APP_ENV` | `development` (default) or `production`. Controls automatic schema setup on backend startup. |
| `POSTGRES_USER` | PostgreSQL username for Docker Compose |
| `POSTGRES_PASSWORD` | PostgreSQL password for Docker Compose |
| `POSTGRES_DB` | PostgreSQL database name |
| `DATABASE_URL` | SQLAlchemy connection string for the backend |
| `TEST_DATABASE_URL` | Optional. Separate PostgreSQL database for backend tests (defaults to `finance_app_test`) |
| `SECRET_KEY` | JWT signing key. Must be changed and at least 32 characters when `APP_ENV=production` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT access token lifetime in minutes |
| `CORS_ORIGINS` | Comma-separated allowed frontend origins (use `http://` locally, `https://` in production) |
| `NEXT_PUBLIC_API_URL` | Browser-accessible backend URL; required at frontend build time and in `frontend/.env.local` for local dev |
| `COOKIE_SECURE` | `false` in development, `true` in production (prepares future httpOnly cookies) |
| `COOKIE_SAMESITE` | Cookie SameSite policy (`lax`, `strict`, or `none`) |
| `COOKIE_HTTPONLY` | Default `true`; used when cookie-based auth is implemented |

For production values, see [`.env.production.example`](.env.production.example).

## Running the Application

### Production-style Docker (full stack)

From the project root:

```bash
docker compose up -d --build
```

This starts PostgreSQL, the FastAPI backend, and the Next.js frontend.

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API docs | http://localhost:8000/docs |
| Health check | http://localhost:8000/health |

Check container status:

```bash
docker compose ps
docker compose logs
```

Stop services:

```bash
docker compose down
docker compose down -v    # also remove persisted database data
```

### Local development (frontend only)

With database and backend running via Docker:

```bash
cd frontend
npm install
cp ../.env.example .env.local
npm run dev
```

The app runs at http://localhost:3000.

### Local development (backend only)

Ensure PostgreSQL is running, then from `backend/`:

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Backend Testing

Tests use **pytest** with an isolated PostgreSQL database. They never run against the development database (`finance_app`).

### Prerequisites

- PostgreSQL must be running (for example via `docker compose up -d postgres`)
- The test database is created automatically on first run if it does not exist (`finance_app_test` by default)

All commands below should be run from the `backend/` directory.

### Activate the virtual environment

Install test dependencies and run `pytest` only after activating the backend virtual environment. If you have not created one yet:

```bash
cd backend
python -m venv .venv
```

Activate the environment before each test session:

**Windows PowerShell:**

```powershell
cd backend
.venv\Scripts\Activate.ps1
```

**Windows CMD:**

```cmd
cd backend
.venv\Scripts\activate.bat
```

**macOS/Linux:**

```bash
cd backend
source .venv/bin/activate
```

Your shell prompt should show `(.venv)` when the environment is active.

### Install test dependencies

With the virtual environment activated, from `backend/`:

```bash
pip install -r requirements-dev.txt
```

### Run tests

With the virtual environment still activated, from `backend/`:

```bash
pytest
```

Or:

```bash
python -m pytest
```

Optional: override the test database URL:

```bash
TEST_DATABASE_URL=postgresql+psycopg://finance_user:finance_pass@localhost:5432/finance_app_test pytest
```

### Test coverage

| Module | Coverage |
|--------|----------|
| `test_auth.py` | Registration, login, password hashing, JWT protected routes |
| `test_transactions.py` | CRUD, category normalization, user isolation |
| `test_budgets.py` | CRUD, case-insensitive progress calculation |
| `test_dashboard.py` | Balance aggregation, monthly filtering, widget limits |

Each test starts with a clean database state. Tables are recreated before every test.

## Continuous Integration

Every push to `main` and every pull request targeting `main` automatically runs the CI pipeline defined in [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

The workflow runs three jobs in parallel:

| Job | What it validates |
|-----|-------------------|
| Backend Tests | Full pytest suite against an isolated PostgreSQL service |
| Frontend Build | `npm ci`, ESLint (if configured), and production `npm run build` |
| Docker Validation | Backend and frontend image builds plus `docker compose config` |

If any job fails, the workflow fails and the push or pull request is blocked until the issue is fixed.

### Reproduce CI checks locally

Run these from the repository root. They mirror what GitHub Actions runs.

**Backend tests** — requires PostgreSQL on port 5432:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # macOS/Linux
# .venv\Scripts\Activate.ps1       # Windows PowerShell

pip install -r requirements-dev.txt

export APP_ENV=development
export SECRET_KEY=ci-secret-key-with-at-least-32-characters
export CORS_ORIGINS=http://localhost:3000
export TEST_DATABASE_URL=postgresql+psycopg://finance_user:finance_pass@localhost:5432/finance_app_test
export DATABASE_URL=$TEST_DATABASE_URL

pytest
```

**Frontend build:**

```bash
cd frontend
npm ci
npm run lint --if-present
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run build
```

**Docker validation:**

```bash
docker build -t finance-app-backend:local ./backend
docker build --build-arg NEXT_PUBLIC_API_URL=http://localhost:8000 -t finance-app-frontend:local ./frontend

POSTGRES_USER=finance_user \
POSTGRES_PASSWORD=finance_pass \
POSTGRES_DB=finance_app \
SECRET_KEY=ci-secret-key-with-at-least-32-characters \
CORS_ORIGINS=http://localhost:3000 \
NEXT_PUBLIC_API_URL=http://localhost:8000 \
docker compose config --quiet
```

## Production Notes

- Set `APP_ENV=production` to skip automatic table creation and startup migrations on the backend.
- Provision the database schema separately before deploying (see [AWS Deployment](#aws-deployment)).
- Change `SECRET_KEY` to a strong random value of at least 32 characters.
- Set `CORS_ORIGINS` to your deployed frontend HTTPS origin(s).
- Set `NEXT_PUBLIC_API_URL` to the browser-accessible backend **HTTPS** URL **before building** the frontend Docker image.
- See [`.env.production.example`](.env.production.example) for all production variables.
- The application is **HTTPS-ready at the code level**. Production URLs must use `https://`. Local development continues to use HTTP.

### HTTPS readiness

The codebase is prepared for HTTPS termination at the ALB:

- Production `CORS_ORIGINS` and `NEXT_PUBLIC_API_URL` must use `https://` domains
- Backend CORS allows credentialed requests (`allow_credentials=True`) for future cookie-based auth
- Cookie security flags (`COOKIE_SECURE`, `COOKIE_SAMESITE`, `COOKIE_HTTPONLY`) are environment-driven
- Frontend API client sends `credentials: "include"` on all requests
- JWT tokens still use `localStorage` today; httpOnly cookie migration is planned during auth hardening

#### Current authentication assumptions (to be addressed in auth hardening)

| Area | Current behavior | Planned change |
|------|------------------|----------------|
| Token storage | `localStorage` via `lib/auth.ts` | httpOnly Secure cookies set by backend |
| Authorization header | `Bearer` token on each request | Cookie-based session or dual support during migration |
| Token refresh | Not implemented | Refresh token rotation |

### Backend production environment

| Variable | Required | Description |
|----------|----------|-------------|
| `APP_ENV` | Yes | Must be `production` in deployed environments |
| `DATABASE_URL` | Yes | PostgreSQL connection string (`postgresql+psycopg://...`) |
| `SECRET_KEY` | Yes | JWT signing key, at least 32 characters, not the default value |
| `CORS_ORIGINS` | Yes | Comma-separated frontend HTTPS origins (e.g. `https://app.example.com`) |
| `COOKIE_SECURE` | Yes (prod) | Must be `true` in production |
| `COOKIE_SAMESITE` | No | `lax` (default), `strict`, or `none` |
| `COOKIE_HTTPONLY` | No | Default `true`; used when cookie auth is implemented |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | JWT lifetime in minutes (default: 10080) |

The backend Docker image listens on `0.0.0.0:8000`. On startup it validates configuration, verifies the database connection, and logs clear errors before exiting if anything fails. The `GET /health` endpoint is public and requires no authentication.

### Frontend production environment

| Variable | Required | When | Description |
|----------|----------|------|-------------|
| `NEXT_PUBLIC_API_URL` | Yes | **Build time** | Public backend URL baked into the Next.js bundle |

`NEXT_PUBLIC_API_URL` is the only source for API URL configuration. It must be set when building the frontend Docker image:

```bash
docker build --build-arg NEXT_PUBLIC_API_URL=https://api.example.com -t finance-frontend ./frontend
```

For local development, set it in `frontend/.env.local` (copy from `.env.example`).

## AWS Deployment

Simple deployment using Docker images on **AWS App Runner** or **ECS Fargate**, with **Amazon RDS PostgreSQL**.

### Required AWS resources

| Resource | Purpose |
|----------|---------|
| Amazon RDS (PostgreSQL 16) | Application database |
| Amazon ECR (2 repositories) | Store backend and frontend Docker images |
| AWS App Runner or ECS Fargate (2 services) | Run backend and frontend containers |
| (Optional) Application Load Balancer | Required for ECS; App Runner provides HTTPS automatically |

### Required environment variables

Copy from [`.env.production.example`](.env.production.example):

| Variable | Service | Notes |
|----------|---------|-------|
| `APP_ENV` | Backend | Set to `production` |
| `DATABASE_URL` | Backend | RDS endpoint with `postgresql+psycopg://` driver |
| `SECRET_KEY` | Backend | Strong random string, 32+ characters |
| `CORS_ORIGINS` | Backend | Your frontend HTTPS URL |
| `NEXT_PUBLIC_API_URL` | Frontend build | Your backend HTTPS URL (build-time only) |
| `COOKIE_SECURE` | Backend | `true` in production |
| `COOKIE_SAMESITE` | Backend | `lax` recommended |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Backend | Optional |

### Deployment steps

1. **Create RDS PostgreSQL**
   - Engine: PostgreSQL 16
   - Note the endpoint, port, database name, username, and password
   - Allow inbound access from your backend service security group

2. **Provision the database schema (one time)**
   - The backend skips automatic schema creation when `APP_ENV=production`
   - Run the backend once with `APP_ENV=development` pointed at RDS to create tables, or apply schema manually
   - After schema exists, deploy with `APP_ENV=production`

3. **Build and push Docker images to ECR**

   ```bash
   # Authenticate to ECR (replace account/region)
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ACCOUNT.dkr.ecr.us-east-1.amazonaws.com

   # Backend
   docker build -t finance-backend ./backend
   docker tag finance-backend:latest ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/finance-backend:latest
   docker push ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/finance-backend:latest

   # Frontend — NEXT_PUBLIC_API_URL must be your deployed backend URL
   docker build --build-arg NEXT_PUBLIC_API_URL=https://api.yourdomain.com -t finance-frontend ./frontend
   docker tag finance-frontend:latest ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/finance-frontend:latest
   docker push ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/finance-frontend:latest
   ```

4. **Deploy backend (App Runner or ECS Fargate)**
   - Image: backend ECR image
   - Port: `8000`
   - Health check path: `/health`
   - Environment variables: `APP_ENV`, `DATABASE_URL`, `SECRET_KEY`, `CORS_ORIGINS`
   - Ensure the service can reach RDS on port 5432

5. **Deploy frontend (App Runner or ECS Fargate)**
   - Image: frontend ECR image (already built with `NEXT_PUBLIC_API_URL`)
   - Port: `3000`
   - No runtime API URL configuration needed — it is baked in at build time

6. **Verify**
   - `GET https://api.yourdomain.com/health` returns `{"status":"ok"}`
   - Open the frontend URL and register/login

### Common failure points

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Backend container exits on startup | Invalid `DATABASE_URL` or RDS not reachable | Check security groups, RDS endpoint, credentials; read container logs |
| Backend starts but frontend API calls fail | Wrong `NEXT_PUBLIC_API_URL` at build time | Rebuild frontend image with correct backend URL |
| CORS errors in browser | `CORS_ORIGINS` missing frontend URL | Add exact frontend origin (including `https://`) to backend env |
| `SECRET_KEY` validation error | Default or short secret in production | Set a unique 32+ character secret |
| 401 on all routes except `/health` | Expected — routes require JWT auth | Register/login via frontend |
| Database tables missing | Schema not provisioned before production deploy | Bootstrap schema once with `APP_ENV=development`, then redeploy with `production` |

## HTTPS Deployment Checklist

Complete these manual AWS steps to enable HTTPS. The application code is already prepared.

1. **Configure a production domain name** for frontend and backend (e.g. `app.example.com`, `api.example.com`).
2. **Request an ACM SSL/TLS certificate** for the domain(s) in the same AWS region as the ALB.
3. **Complete ACM DNS validation** by adding the required CNAME records.
4. **Add an HTTPS listener (port 443)** to the Application Load Balancer.
5. **Attach the ACM certificate** to the HTTPS listener.
6. **Configure the HTTP (port 80) listener** to redirect all traffic to HTTPS.
7. **Configure DNS** (Route 53 or external provider) to point the domain(s) to the ALB.
8. **Update ECS environment variables:**
   - `NEXT_PUBLIC_API_URL` — rebuild frontend image with `https://` backend URL
   - `CORS_ORIGINS` — set to `https://` frontend domain
   - `COOKIE_SECURE=true` on backend
9. **Redeploy ECS services** (push to `main` or run the Deploy workflow).
10. **Verify:**
    - `https://` frontend and backend load successfully
    - HTTP redirects to HTTPS
    - Frontend communicates with backend (register/login, dashboard)
    - No CORS errors in browser console
    - ALB target groups report healthy

## Continuous Deployment

Pushes to `main` automatically deploy to AWS ECS after CI passes. CD is a separate workflow from CI and does not modify the existing [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

### How CD works

```
git push main
      |
      v
CI workflow (ci.yml) — backend tests, frontend build, Docker validation
      |
      v (on success)
Deploy workflow (deploy.yml)
      |
      +-- Build backend Docker image → tag with commit SHA → push to ECR
      +-- Build frontend Docker image → tag with commit SHA → push to ECR
      +-- Update backend ECS task definition → deploy → wait for stability
      +-- Verify backend /health endpoint
      +-- Update frontend ECS task definition → deploy → wait for stability
      +-- Verify frontend URL responds
```

Image tags use the full Git commit SHA, for example:

- `ACCOUNT.dkr.ecr.REGION.amazonaws.com/BACKEND_REPO:abc123def456...`
- `ACCOUNT.dkr.ecr.REGION.amazonaws.com/FRONTEND_REPO:abc123def456...`

Task definitions are read from the currently running ECS services, updated with the new image tag, registered, and deployed. No task definition names need to be hardcoded in the workflow.

### Required GitHub repository secrets

| Secret | Description |
|--------|-------------|
| `AWS_ACCESS_KEY_ID` | IAM user access key for deployment |
| `AWS_SECRET_ACCESS_KEY` | IAM user secret key for deployment |

Store these under **Settings → Secrets and variables → Actions → Secrets**.

> **Recommended upgrade:** Replace long-lived access keys with GitHub OIDC and an IAM role. That requires additional AWS and GitHub configuration not included in this workflow.

### Required GitHub repository variables

Configure these under **Settings → Secrets and variables → Actions → Variables**:

| Variable | Description | Example |
|----------|-------------|---------|
| `AWS_REGION` | AWS region for ECR and ECS | `us-east-1` |
| `ECR_BACKEND_REPOSITORY` | ECR repository name for backend | `finance-backend` |
| `ECR_FRONTEND_REPOSITORY` | ECR repository name for frontend | `finance-frontend` |
| `ECS_CLUSTER` | ECS cluster name | `finance-cluster` |
| `ECS_BACKEND_SERVICE` | Backend ECS service name | `finance-backend-service` |
| `ECS_FRONTEND_SERVICE` | Frontend ECS service name | `finance-frontend-service` |
| `ECS_BACKEND_CONTAINER_NAME` | Container name in backend task definition | from ECS console |
| `ECS_FRONTEND_CONTAINER_NAME` | Container name in frontend task definition | from ECS console |
| `NEXT_PUBLIC_API_URL` | Public backend URL (frontend build arg) | `https://api.yourdomain.com` |
| `BACKEND_HEALTH_URL` | Backend health check URL | `https://api.yourdomain.com/health` |
| `FRONTEND_URL` | Public frontend URL | `https://app.yourdomain.com` |

**These values are not in the repository.** Copy them from your AWS console and ALB DNS names before the first automated deploy.

### Required AWS IAM permissions

The deployment IAM user or role needs at minimum:

| Service | Permissions |
|---------|-------------|
| ECR | `GetAuthorizationToken`, `BatchCheckLayerAvailability`, `GetDownloadUrlForLayer`, `BatchGetImage`, `PutImage`, `InitiateLayerUpload`, `UploadLayerPart`, `CompleteLayerUpload` |
| ECS | `DescribeServices`, `DescribeTaskDefinition`, `RegisterTaskDefinition`, `UpdateService` |
| STS | `GetCallerIdentity` |

Example policy scope: ECR repositories and ECS cluster/services used by this project only.

### Manual trigger and retry

To redeploy without a new commit:

1. Open **Actions → Deploy → Run workflow**
2. Select the `main` branch
3. Click **Run workflow**

`workflow_dispatch` skips the CI gate. Use this to retry a failed deployment or redeploy the current `main` commit. For normal releases, push to `main` and let CI trigger CD automatically.

### Troubleshooting failed deployments

| Failure stage | What to check |
|---------------|---------------|
| Validate deployment configuration | All repository variables and secrets listed above are set |
| Build and push | Dockerfile errors; ECR repository exists; IAM has ECR push permissions |
| Deploy to ECS | Container name matches task definition; IAM has ECS update permissions |
| Wait for service stability | ECS service events; task logs in CloudWatch; security groups; RDS connectivity |
| Backend health check | `BACKEND_HEALTH_URL` is correct; ALB target group healthy; backend task running |
| Frontend availability | `FRONTEND_URL` is correct; frontend task running; `NEXT_PUBLIC_API_URL` matches backend URL |

View ECS service events:

```bash
aws ecs describe-services \
  --cluster YOUR_CLUSTER \
  --services YOUR_SERVICE \
  --query 'services[0].events[:5]'
```

View failed task logs in CloudWatch Logs for the service's log group.

## Folder Structure

```
/
├── PROJECT_STATUS.md
├── README.md
├── docker-compose.yml
├── .env.example
├── .env.production.example
├── frontend/          Next.js application
├── backend/           FastAPI application
│   └── tests/         pytest test suite (isolated test database)
└── .github/workflows/
    ├── ci.yml         GitHub Actions CI pipeline
    └── deploy.yml     GitHub Actions CD pipeline (ECS deploy)
```

## Stopping Services

```bash
docker compose down
docker compose down -v    # Stop and remove persisted data
```
