# Deployment

Copy `.env.example` to `.env`, set secrets, then run `docker compose up -d`. Docker starts API, PostgreSQL, Redis, and Qdrant with persistent named volumes and health checks.

Run the reload-enabled service with `docker compose --profile dev up api-dev postgres redis qdrant`. Never commit `.env`; use a secret manager in production. Set `DEBUG=false`, a strong `SECRET_KEY`, and production CORS origins before exposing the API.
