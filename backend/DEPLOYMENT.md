# RAAHAT Backend Deployment Guide

This document outlines the deployment requirements for the RAAHAT FastAPI Backend to ensure a resilient, secure, and fully functional production or demo environment.

## 1. Required Environment Variables

For production or demo deployment, the following environment variables **must** be set:

| Variable | Description |
|---|---|
| `ENVIRONMENT` | Must be set to `production` (disables auto-reload and forces `AUTH_DISABLED=False` unless overridden). |
| `DATABASE_URL` | The PostgreSQL connection string. Must use the async driver (e.g., `postgresql+asyncpg://user:pass@host:port/db`). |
| `CORS_ORIGINS` | Comma-separated list of allowed frontend URLs (e.g., `https://myfrontend.web.app,https://another.url.com`). |
| `PORT` | The port the application binds to (dynamically assigned by PaaS platforms like Cloud Run or Heroku). |

### Feature Configuration Keys

| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | Required for AI generation fallback and RAG. |
| `GOOGLE_PLACES_API_KEY` | (Optional) Primary provider for nearby services. |
| `GOOGLE_ROUTES_API_KEY` | (Optional) Primary provider for safe routing. |
| `GEOAPIFY_API_KEY` | (Optional) Fallback map provider. |

### Advanced Overrides

| Variable | Description |
|---|---|
| `AUTH_DISABLED` | Set to `false` explicitly to enforce JWT Firebase authentication. Set to `true` strictly for local testing. |
| `USE_MOCKS` | Set to `true` to use mock provider data if external APIs rate-limit during the demo. |

## 2. Infrastructure Requirements

The application requires a **PostgreSQL** database with the following extensions installed:
- `postgis` (for geographical location capabilities)
- `vector` (pgvector, for RAG embeddings)

To run the Alembic migrations, ensure the production database is reachable and the extensions are manually created before the first migration runs:
```sql
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS vector;
```

## 3. Runtime & Startup

- **Python Version:** Python 3.12+
- **Startup Command:**
  To start the server securely, use standard uvicorn invocation:
  ```bash
  uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```
  *(Note: Running `python -m app.main` is supported for local environments but will respect the `PORT` env var and automatically disable reload if `ENVIRONMENT=production`.)*

## 4. Database Health Check

The backend features a lightweight database connectivity check on startup (`lifespan` hook). 
- If the database is unreachable, the application **will still boot up**. 
- It will mark the database as unhealthy and log a critical error, while gracefully failing on `/api/v1/health` with a 503 status code. 
- This prevents container crash-loops on platforms like Cloud Run, ensuring the application remains diagnosable during transient infrastructure failures.
