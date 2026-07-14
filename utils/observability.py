"""Optional, vendor-neutral tracing and Prometheus instrumentation."""

from __future__ import annotations

import os
from contextlib import contextmanager
from time import perf_counter
from typing import Iterator

from ..configs.settings import settings


class Observability:
    """Initializes optional telemetry once and exposes safe span helpers."""

    def __init__(self) -> None:
        self._initialized = False
        self._tracer = None
        self._request_counter = None
        self._duration_histogram = None

    def initialize(self, app=None) -> None:
        """Configure LangSmith, OpenTelemetry, and Prometheus when enabled."""
        if self._initialized:
            return
        self._configure_langsmith()
        if settings.otel_enabled:
            self._configure_otel(app)
        if settings.metrics_enabled:
            self._configure_prometheus(app)
        self._initialized = True

    def _configure_langsmith(self) -> None:
        if not settings.langsmith_tracing:
            return
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        if settings.langsmith_api_key:
            os.environ["LANGCHAIN_API_KEY"] = settings.langsmith_api_key
        os.environ["LANGCHAIN_PROJECT"] = settings.langchain_project
        os.environ["LANGCHAIN_ENDPOINT"] = settings.langsmith_endpoint

    def _configure_otel(self, app) -> None:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        provider = TracerProvider(resource=Resource.create({"service.name": settings.otel_service_name}))
        provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=settings.otel_exporter_otlp_endpoint, insecure=True)))
        trace.set_tracer_provider(provider)
        self._tracer = trace.get_tracer(settings.otel_service_name)
        if app is not None:
            FastAPIInstrumentor.instrument_app(app)

    def _configure_prometheus(self, app) -> None:
        from prometheus_client import Counter, Histogram, make_asgi_app

        self._request_counter = Counter("multi_agent_events_total", "Application events", ["operation", "outcome"])
        self._duration_histogram = Histogram("multi_agent_operation_seconds", "Operation duration", ["operation"])
        if app is not None:
            app.mount(settings.metrics_path, make_asgi_app())

    @contextmanager
    def span(self, operation: str, **attributes: object) -> Iterator[None]:
        """Record duration, error outcome, and an OTEL span if configured."""
        started = perf_counter()
        span_context = self._tracer.start_as_current_span(operation) if self._tracer else None
        try:
            if span_context:
                with span_context as active_span:
                    for key, value in attributes.items():
                        active_span.set_attribute(key, str(value))
                    yield
            else:
                yield
            if self._request_counter:
                self._request_counter.labels(operation, "success").inc()
        except Exception:
            if self._request_counter:
                self._request_counter.labels(operation, "error").inc()
            raise
        finally:
            if self._duration_histogram:
                self._duration_histogram.labels(operation).observe(perf_counter() - started)


observability = Observability()
