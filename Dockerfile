# syntax=docker/dockerfile:1.7
FROM python:3.11-slim AS builder

WORKDIR /build
ENV PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends gcc g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python -m venv /opt/venv && /opt/venv/bin/pip install -r requirements.txt

FROM python:3.11-slim AS production

RUN addgroup --system app && adduser --system --ingroup app app
WORKDIR /app
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ENVIRONMENT=production

COPY --from=builder /opt/venv /opt/venv
COPY --chown=app:app . .
RUN mkdir -p /app/logs && chown -R app:app /app/logs

USER app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)"

CMD ["uvicorn", "multi_agent_system.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM production AS development
USER root
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
USER app
CMD ["uvicorn", "multi_agent_system.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
