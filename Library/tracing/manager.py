import asyncio
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
    SpanExporter,
)
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.trace import set_span_in_context, get_current_span
from .metrics import record_trace_collected, record_trace_exported, record_trace_export_failed
from Library.logging import get_logger

logger = get_logger(__name__)

class TracingManager:
    def __init__(self, service_name: str, otlp_endpoint: str = None):
        self.service_name = service_name
        self.otlp_endpoint = otlp_endpoint
        self.tracer_provider = None
        self.tracer = None
        self.span_processor = None

    async def setup(self):
        try:
            resource = Resource.create({"service.name": self.service_name})
            self.tracer_provider = TracerProvider(resource=resource)
            
            # Configure exporter
            exporter: SpanExporter
            if self.otlp_endpoint:
                exporter = OTLPSpanExporter(endpoint=self.otlp_endpoint)
            else:
                exporter = ConsoleSpanExporter()
                logger.warning("Using console exporter - not suitable for production")
            
            # Create batch processor
            self.span_processor = BatchSpanProcessor(exporter)
            self.tracer_provider.add_span_processor(self.span_processor)
            
            # Set global tracer
            trace.set_tracer_provider(self.tracer_provider)
            self.tracer = trace.get_tracer(self.service_name)
            
            logger.info("Tracing setup complete")
        except Exception as e:
            logger.error(f"Tracing setup failed: {e}", exc_info=True)
            raise

    async def shutdown(self):
        try:
            if self.span_processor:
                await asyncio.to_thread(self.span_processor.shutdown)
            logger.info("Tracing shutdown complete")
        except Exception as e:
            logger.error(f"Tracing shutdown failed: {e}", exc_info=True)

    def get_tracer(self):
        return self.tracer

    def start_span(self, name: str, context: dict = None):
        try:
            return self.tracer.start_as_current_span(name, context=context)
        except Exception as e:
            logger.error(f"Span start failed: {e}", exc_info=True)
            record_trace_export_failed()
            raise

    def inject_context(self, headers: dict):
        from opentelemetry.propagate import inject
        try:
            inject(headers)
            return headers
        except Exception as e:
            logger.error(f"Context injection failed: {e}", exc_info=True)
            return headers

    def extract_context(self, headers: dict):
        from opentelemetry.propagate import extract
        try:
            return extract(headers)
        except Exception as e:
            logger.error(f"Context extraction failed: {e}", exc_info=True)
            return None
