# Docker & Docker Compose Setup Guide

This directory contains the Docker configuration and multi-service orchestration definitions for the **Multi-Agent System**.

---

## 1. Services Architecture

The Docker Compose stack orchestrates the following services:

| Service | Container Image / Target | Internal Port | Host Port | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **`frontend`** | `frontend/Dockerfile` (production) | `3000` | `3000` | Next.js execution dashboard & telemetry UI |
| **`api`** | `Dockerfile` (production) | `8000` | `8000` | FastAPI Multi-Agent Supervisor & orchestrator |
| **`api-dev`** | `Dockerfile` (development) | `8000` | `8000` | Dev container with live autoreload (`--profile dev`) |
| **`postgres`** | `postgres:16-alpine` | `5432` | `5432` | Long-term persistent execution storage & user state |
| **`redis`** | `redis:7-alpine` | `6379` | `6379` | In-memory cache, task locks, & session conversation |
| **`qdrant`** | `qdrant/qdrant:v1.7.4` | `6333` / `6334` | `6333` | Vector database for RAG document chunk search |
| **`prometheus`** *(opt)* | `prom/prometheus:latest` | `9090` | `9090` | Time-series metrics scraper for `/metrics/prometheus` |
| **`grafana`** *(opt)* | `grafana/grafana:latest` | `3000` | `3001` | Visualization dashboards for system telemetry |

---

## 2. Quick Start

### Step 1: Prepare Environment Variables
Copy `.env.example` to `.env` in the repository root and configure your API keys:

```bash
cp .env.example .env
```

Ensure your LLM credentials are set:
```dotenv
DEFAULT_LLM_PROVIDER=openrouter
DEFAULT_MODEL=nvidia/nemotron-3-ultra-550b-a55b:free
OPENROUTER_API_KEY=your-openrouter-key
# OR for OpenAI:
# DEFAULT_LLM_PROVIDER=openai
# OPENAI_API_KEY=your-openai-key
```

### Step 2: Start the Production Stack
Run from repository root:

```bash
# Build and launch all core services in the background
docker compose up -d --build
```

Access the interfaces:
- **Frontend Dashboard:** [http://localhost:3000](http://localhost:3000)
- **FastAPI OpenAPI Docs:** [http://localhost:8000/api/docs](http://localhost:8000/api/docs)
- **API Health Check:** [http://localhost:8000/health](http://localhost:8000/health)
- **Qdrant Dashboard:** [http://localhost:6333/dashboard](http://localhost:6333/dashboard)

---

## 3. Development Mode (Hot Reloading)

For active backend and frontend development with source code mounted from your host:

```bash
docker compose --profile dev up --build
```

This runs `api-dev` with Uvicorn reload enabled and `frontend-dev` with Next.js fast-refresh.

---

## 4. Observability Stack (Prometheus & Grafana)

To run the extended stack with Prometheus and Grafana metrics:

```bash
docker compose -f docker/docker-compose.yml up -d
```

- **Prometheus UI:** [http://localhost:9090](http://localhost:9090)
- **Grafana UI:** [http://localhost:3001](http://localhost:3001) (Default user: `admin`, password: `admin` or `${GRAFANA_ADMIN_PASSWORD}`)

---

## 5. Useful Docker Commands

```bash
# View aggregated real-time logs
docker compose logs -f

# View logs for a specific service
docker compose logs -f api
docker compose logs -f frontend

# Check health and status of containers
docker compose ps

# Execute an interactive shell inside the API container
docker compose exec api /bin/bash

# Connect to the PostgreSQL database CLI
docker compose exec postgres psql -U multi_agent -d multi_agent

# Connect to Redis CLI
docker compose exec redis redis-cli ping

# Stop all containers
docker compose down

# Stop all containers and wipe persistent volumes (CAUTION: deletes DB data)
docker compose down -v
```

---

## 6. Health Checks & Startup Order

All dependent services utilize Docker native health checks:
1. `postgres` verifies database readiness (`pg_isready`).
2. `redis` verifies ping response (`redis-cli ping`).
3. `qdrant` checks process responsiveness.
4. `api` waits until database, cache, and vector store are healthy before starting.
5. `frontend` waits until `api` passes its healthcheck at `/health`.

---

## 7. Persistent Named Volumes

- `postgres_data`: Durable PostgreSQL table storage (`/var/lib/postgresql/data`)
- `redis_data`: Redis AOF persistence files (`/data`)
- `qdrant_data`: Qdrant vector index and payload storage (`/qdrant/storage`)
- `app_logs`: Shared application logging files (`/app/logs`)
