# core/observability.py

import os
from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.prometheus import PrometheusMetricsExporter
from opentelemetry.sdk.metrics import MeterProvider
from prometheus_client import start_http_server

from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

import logging

logger = logging.getLogger(__name__)

class Observability:
    def __init__(
        self,
        service_name: str,
        tracing_enabled: bool = True,
        prometheus_port: int = 9464,
        otlp_endpoint: str = "http://localhost:4317"
    ):
        # Resource labeling for both traces and metrics
        resource = Resource.create({"service.name": service_name})

        # --- Tracing ---
        if tracing_enabled:
            trace.set_tracer_provider(TracerProvider(resource=resource))
            tracer_provider = trace.get_tracer_provider()
            otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
            span_processor = BatchSpanProcessor(otlp_exporter)
            tracer_provider.add_span_processor(span_processor)
            self.tracer = trace.get_tracer(service_name)
            logger.info("Tracing enabled and OTLP exporter configured.")
        else:
            self.tracer = None
            logger.info("Tracing is disabled.")

        # --- Metrics ---
        # Start Prometheus metrics HTTP server
        start_http_server(port=prometheus_port, addr="0.0.0.0")
        metrics.set_meter_provider(MeterProvider(resource=resource))
        self.meter = metrics.get_meter(service_name)
        self.prometheus_exporter = PrometheusMetricsExporter()
        metrics.get_meter_provider().start_pipeline(
            self.meter, self.prometheus_exporter, 5
        )
        logger.info(f"Prometheus metrics exporter started on port {prometheus_port}")

    def get_tracer(self):
        return self.tracer

    def get_meter(self):
        return self.meter

# Usage example:
# observability = Observability(service_name="myservice")
# tracer = observability.get_tracer()
# meter = observability.get_meter()
