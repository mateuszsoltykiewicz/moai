# utils/prometheus_instrumentation.py

from prometheus_client import Counter, Gauge, Histogram, Summary, CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST
from typing import Optional, Dict

from prometheus_client import CollectorRegistry

# Shared registry for all metrics in the platform
REGISTRY = CollectorRegistry()

class MetricsManager:
    def __init__(self, app_name: str, registry: Optional[CollectorRegistry] = None):
        self.app_name = app_name
        self.registry = registry or CollectorRegistry()
        self.metrics: Dict[str, object] = {}

    def counter(self, name, documentation, labelnames=()):
        fq_name = f"{self.app_name}_{name}"
        metric = Counter(fq_name, documentation, labelnames, registry=self.registry)
        self.metrics[fq_name] = metric
        return metric

    def gauge(self, name, documentation, labelnames=()):
        fq_name = f"{self.app_name}_{name}"
        metric = Gauge(fq_name, documentation, labelnames, registry=self.registry)
        self.metrics[fq_name] = metric
        return metric

    def histogram(self, name, documentation, labelnames=()):
        fq_name = f"{self.app_name}_{name}"
        metric = Histogram(fq_name, documentation, labelnames, registry=self.registry)
        self.metrics[fq_name] = metric
        return metric

    def summary(self, name, documentation, labelnames=()):
        fq_name = f"{self.app_name}_{name}"
        metric = Summary(fq_name, documentation, labelnames, registry=self.registry)
        self.metrics[fq_name] = metric
        return metric

    def expose_metrics_fastapi(self, app, path="/metrics"):
        from fastapi import Response

        @app.get(path, include_in_schema=False)
        async def metrics():
            data = generate_latest(self.registry)
            return Response(content=data, media_type=CONTENT_TYPE_LATEST)

