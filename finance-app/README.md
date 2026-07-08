# Finance App

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

1. Navigate to the project root:

   ```bash
   cd finance-app
   ```

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
| `SECRET_KEY` | JWT signing key. Must be changed and at least 32 characters when `APP_ENV=production` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT access token lifetime in minutes |
| `CORS_ORIGINS` | Comma-separated allowed frontend origins |
| `NEXT_PUBLIC_API_URL` | Browser-accessible backend URL used by the frontend |

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

## Production Notes

- Set `APP_ENV=production` to skip automatic table creation and startup migrations on the backend.
- Provision the database schema separately before deploying (Alembic is recommended for future use).
- Change `SECRET_KEY` to a strong random value of at least 32 characters.
- Set `CORS_ORIGINS` to your deployed frontend origin(s).
- Set `NEXT_PUBLIC_API_URL` to the browser-accessible backend URL before building the frontend Docker image.

## Folder Structure

```
finance-app/
├── frontend/          Next.js application
├── backend/           FastAPI application
├── docker-compose.yml PostgreSQL + backend + frontend
├── .env.example       Environment template
├── PROJECT_STATUS.md  Implementation status
└── README.md
```

## Stopping Services

```bash
docker compose down
docker compose down -v    # Stop and remove persisted data
```
