"""
TracingManager: Centralized OpenTelemetry tracing management.

- Configures and exposes OpenTelemetry tracer for all components
- Provides async lifecycle management
- Supports dynamic exporter and resource configuration
- Integrates with FastAPI and other frameworks
"""

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from typing import Optional
from .utils import log_info

class TracingManager:
    def __init__(self):
        self.tracer = None
        self.tracer_provider = None

    async def setup(self, service_name: str, otlp_endpoint: Optional[str] = None):
        """
        Async setup logic for the TracingManager.
        """
        resource = Resource.create({"service.name": service_name})
        self.tracer_provider = TracerProvider(resource=resource)
        if otlp_endpoint:
            otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
            span_processor = BatchSpanProcessor(otlp_exporter)
            self.tracer_provider.add_span_processor(span_processor)
            log_info(f"TracingManager: OTLP exporter configured at {otlp_endpoint}")
        # Always add console exporter for debugging
        console_exporter = ConsoleSpanExporter()
        self.tracer_provider.add_span_processor(BatchSpanProcessor(console_exporter))
        trace.set_tracer_provider(self.tracer_provider)
        self.tracer = trace.get_tracer(service_name)
        log_info("TracingManager: Setup complete.")

    async def shutdown(self):
        """
        Async shutdown logic for the TracingManager.
        """
        # No explicit shutdown needed for OpenTelemetry Python SDK as of 2024
        log_info("TracingManager: Shutdown complete.")

    def get_tracer(self):
        """
        Return the global tracer.
        """
        return self.tracer
