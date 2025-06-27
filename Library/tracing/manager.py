import asyncio
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider, ReadableSpan
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
    SpanExporter,
)
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.trace import SpanContext, set_span_in_context, get_current_span
from .metrics import record_trace_collected, record_trace_exported, record_trace_export_failed
from .utils import log_info, log_error

class TracingManager:
    def __init__(self, service_name: str, otlp_endpoint: str = None):
        self.service_name = service_name
        self.otlp_endpoint = otlp_endpoint
        self.tracer_provider = None
        self.tracer = None
        self.span_processor = None

    async def setup(self):
        resource = Resource.create({"service.name": self.service_name})
        self.tracer_provider = TracerProvider(resource=resource)
        exporter: SpanExporter
        if self.otlp_endpoint:
            exporter = OTLPSpanExporter(endpoint=self.otlp_endpoint)
        else:
            exporter = ConsoleSpanExporter()
        self.span_processor = BatchSpanProcessor(exporter)
        self.tracer_provider.add_span_processor(self.span_processor)
        trace.set_tracer_provider(self.tracer_provider)
        self.tracer = trace.get_tracer(self.service_name)
        log_info("TracingManager: Setup complete.")

    async def shutdown(self):
        if self.span_processor:
            self.span_processor.shutdown()
        log_info("TracingManager: Shutdown complete.")

    def get_tracer(self):
        return self.tracer

    def start_span(self, name: str, context: SpanContext = None):
        return self.tracer.start_as_current_span(name, context=context)

    def inject_context(self, headers: dict):
        from opentelemetry.propagate import inject
        inject(headers)
        return headers

    def extract_context(self, headers: dict):
        from opentelemetry.propagate import extract
        return extract(headers)
