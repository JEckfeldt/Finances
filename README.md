# Finance App

A production-quality personal finance application monorepo. This repository provides the foundational architecture for a full-stack finance app with a Next.js frontend, FastAPI backend, and PostgreSQL database.

## Technology Stack

| Layer    | Technologies |
|----------|--------------|
| Frontend | Next.js 15, TypeScript, Tailwind CSS, shadcn/ui, React Hook Form, Zod, Lucide React, Recharts |
| Backend  | FastAPI, Uvicorn, SQLAlchemy 2.x, Alembic, Pydantic, python-jose, passlib, psycopg |
| Database | PostgreSQL 16 |

## Folder Structure

```
finance-app/
├── frontend/           # Next.js application
├── backend/
│   ├── app/
│   │   ├── main.py     # FastAPI application entry point
│   │   ├── api/        # API route modules
│   │   ├── core/       # Configuration and shared utilities
│   │   ├── models/     # SQLAlchemy models
│   │   ├── schemas/    # Pydantic schemas
│   │   ├── services/   # Business logic
│   │   └── db/         # Database session and migrations
│   └── requirements.txt
├── docker-compose.yml  # PostgreSQL service
├── .env.example        # Environment variable template
├── .gitignore
└── README.md
```

## Prerequisites

- [Node.js](https://nodejs.org/) 18.18 or later
- [Python](https://www.python.org/) 3.11 or later
- [Docker](https://www.docker.com/) and Docker Compose

## Installation

1. Clone the repository and navigate to the project root:

   ```bash
   cd finance-app
   ```

2. Copy the environment template and fill in your values:

   ```bash
   cp .env.example .env
   ```

3. Install frontend dependencies:

   ```bash
   cd frontend
   npm install
   ```

4. Install backend dependencies:

   ```bash
   cd ../backend
   python -m venv .venv

   # Windows
   .venv\Scripts\activate

   # macOS / Linux
   source .venv/bin/activate

   pip install -r requirements.txt
   ```

## Starting the Frontend

From the `frontend/` directory:

```bash
npm run dev
```

The development server runs at [http://localhost:3000](http://localhost:3000).

## Starting the Backend

From the `backend/` directory with your virtual environment activated:

```bash
uvicorn app.main:app --reload
```

The API server runs at [http://localhost:8000](http://localhost:8000).

## Starting PostgreSQL with Docker Compose

From the project root, ensure your `.env` file contains `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB`, then start the database:

```bash
docker compose up -d
```

PostgreSQL is exposed on port `5432`. Data is persisted in the `postgres_data` Docker volume.

To stop the database:

```bash
docker compose down
```

To stop and remove persisted data:

```bash
docker compose down -v
```
