"""
Async Distributed Tracing Integration (OpenTelemetry)

Features:
- Async context manager for spans
- Configurable via environment variables or arguments
- OTLP exporter support (Jaeger, Tempo, etc.)
- No-op fallback if tracing is disabled or OpenTelemetry is not installed
- Ready for integration with async frameworks (FastAPI, aiohttp, etc.)
"""

import os
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager

try:
    from opentelemetry import trace
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    _OTEL_AVAILABLE = True
except ImportError:
    _OTEL_AVAILABLE = False

import logging
logger = logging.getLogger(__name__)


class AsyncTracer:
    """
    Async distributed tracing manager.
    """
    def __init__(
        self,
        service_name: str,
        enabled: Optional[bool] = None,
        otlp_endpoint: Optional[str] = None,
        otlp_headers: Optional[Dict[str, str]] = None,
    ):
        """
        Args:
            service_name: Name of the service for trace resource labeling.
            enabled: Enable tracing (default: env TRACING_ENABLED or True if OTEL installed).
            otlp_endpoint: OTLP collector endpoint (default: env OTEL_EXPORTER_OTLP_ENDPOINT).
            otlp_headers: Dict of headers for OTLP exporter.
        """
        self.service_name = service_name
        self.enabled = enabled if enabled is not None else (
            os.getenv("TRACING_ENABLED", "1") == "1" and _OTEL_AVAILABLE
        )
        self.otlp_endpoint = otlp_endpoint or os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
        self.otlp_headers = otlp_headers or {}

        self._tracer = None
        if self.enabled and _OTEL_AVAILABLE:
            self._setup_tracer()
        elif not _OTEL_AVAILABLE and self.enabled:
            logger.warning("Tracing requested but OpenTelemetry is not installed. Tracing is disabled.")

    def _setup_tracer(self):
        resource = Resource.create({"service.name": self.service_name})
        provider = TracerProvider(resource=resource)
        otlp_exporter = OTLPSpanExporter(endpoint=self.otlp_endpoint, headers=self.otlp_headers)
        span_processor = BatchSpanProcessor(otlp_exporter)
        provider.add_span_processor(span_processor)
        trace.set_tracer_provider(provider)
        self._tracer = trace.get_tracer(self.service_name)
        logger.info(f"Tracing initialized for {self.service_name} (endpoint: {self.otlp_endpoint})")

    def get_tracer(self):
        """
        Returns the tracer instance, or None if tracing is disabled.
        """
        return self._tracer

    @asynccontextmanager
    async def start_span(self, name: str, attributes: Optional[Dict[str, Any]] = None):
        """
        Async context manager for a tracing span.
        Usage:
            async with tracer.start_span("my-operation"):
                ... # your async code
        """
        if self._tracer:
            with self._tracer.start_as_current_span(name) as span:
                if attributes:
                    for k, v in attributes.items():
                        span.set_attribute(k, v)
                yield span
        else:
            # No-op context manager for disabled tracing
            yield None

# Example usage:
# tracer = AsyncTracer("myservice")
# async with tracer.start_span("important-operation", {"user_id": 123}):
#     await do_async_work()
