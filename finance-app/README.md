# Finance App

A personal finance management platform with a clean, modern dashboard aesthetic. Users can view their financial overview, manage transactions, and track budgets.

> **Project state:** See [PROJECT_STATUS.md](./PROJECT_STATUS.md) for a full breakdown of what is and is not implemented.

## Technology Stack

| Layer    | Technologies |
|----------|--------------|
| Frontend | Next.js 15, TypeScript, Tailwind CSS, shadcn/ui, React Hook Form, Zod, Lucide React, Recharts |
| Backend  | FastAPI, Uvicorn, SQLAlchemy 2.x, Alembic, Pydantic, python-jose, passlib, psycopg |
| Database | PostgreSQL 16 |

## Folder Structure

```
finance-app/
├── frontend/
│   ├── app/
│   │   ├── (main)/          # App shell with navigation
│   │   │   ├── dashboard/
│   │   │   ├── transactions/
│   │   │   └── budgets/
│   │   └── page.tsx         # Redirects to /dashboard
│   ├── components/
│   │   ├── dashboard/       # Dashboard placeholder widgets
│   │   ├── layout/          # App shell and sidebar navigation
│   │   ├── transactions/    # Transaction list and form
│   │   └── ui/              # shadcn/ui components
│   └── lib/                 # API client and types
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/             # Routes and dependencies
│   │   ├── core/            # Config and auth (JWT-ready)
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/
│   │   └── db/              # Database session
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml       # PostgreSQL + backend services
├── .env.example
├── .gitignore
└── README.md
```

## Prerequisites

- [Node.js](https://nodejs.org/) 18.18 or later
- [Python](https://www.python.org/) 3.11 or later
- [Docker](https://www.docker.com/) and Docker Compose

## Installation

1. Navigate to the project root:

   ```bash
   cd finance-app
   ```

2. Copy the environment template:

   ```bash
   cp .env.example .env
   ```

3. Install frontend dependencies:

   ```bash
   cd frontend
   npm install
   cp ../.env.example .env.local   # or set NEXT_PUBLIC_API_URL
   ```

4. Install backend dependencies (optional if using Docker for backend):

   ```bash
   cd ../backend
   python -m venv .venv
   .venv\Scripts\activate        # Windows
   pip install -r requirements.txt
   ```

## Starting Services

### PostgreSQL and Backend (Docker)

From the project root:

```bash
docker compose up -d --build
```

- PostgreSQL: `localhost:5432`
- Backend API: [http://localhost:8000](http://localhost:8000)
- Health check: [http://localhost:8000/health](http://localhost:8000/health)

### Frontend (local dev)

From the `frontend/` directory:

```bash
npm run dev
```

The app runs at [http://localhost:3000](http://localhost:3000) and redirects to `/dashboard`.

### Backend (local dev, without Docker)

Ensure PostgreSQL is running, then from `backend/`:

```bash
uvicorn app.main:app --reload
```

## API Endpoints

| Method | Endpoint        | Description              |
|--------|-----------------|--------------------------|
| GET    | `/health`       | Health check             |
| GET    | `/transactions` | List user transactions   |
| POST   | `/transactions` | Create a transaction   |

## Pages

| Route           | Status                                      |
|-----------------|---------------------------------------------|
| `/dashboard`    | Layout with placeholder financial widgets   |
| `/transactions` | Full create and view implementation         |
| `/budgets`      | Skeleton with placeholder budget cards      |

## Stopping Services

```bash
docker compose down       # Stop containers
docker compose down -v    # Stop and remove persisted data
```
