# Observability

Structured JSON logging is enabled with `STRUCTURED_LOGGING=true`. The in-process collector records token estimates, costs, latency, retries, agent and tool outcomes at `/api/v1/metrics`.

Set `METRICS_ENABLED=true` for Prometheus exposition at `METRICS_PATH` (default `/metrics/prometheus`). Set `OTEL_ENABLED=true` and `OTEL_EXPORTER_OTLP_ENDPOINT` to export FastAPI and custom execution spans. Set `LANGSMITH_TRACING=true` and `LANGSMITH_API_KEY` to enable LangSmith tracing. All integrations are opt-in and do not require external services when disabled.
