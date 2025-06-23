"""
MetricsManager: Centralized Prometheus/OpenMetrics management.

- Registers and exposes metrics for all components
- Provides async lifecycle management
- Integrates with FastAPI for /metrics endpoint
- Supports custom metrics and labels
"""

from prometheus_client import (
    CollectorRegistry, Counter, Gauge, Histogram, Summary, generate_latest, CONTENT_TYPE_LATEST
)
from typing import Dict, Any, Optional
import asyncio
from .utils import log_info

class MetricsManager:
    def __init__(self):
        self.registry = CollectorRegistry()
        self.metrics: Dict[str, Any] = {}
        self._lock = asyncio.Lock()

    async def setup(self):
        """
        Async setup logic for the MetricsManager.
        """
        log_info("MetricsManager: Setup complete.")

    async def shutdown(self):
        """
        Async shutdown logic for the MetricsManager.
        """
        log_info("MetricsManager: Shutdown complete.")

    def register_counter(self, name: str, description: str, labelnames: Optional[list] = None):
        """
        Register a new Counter metric.
        """
        with self._lock:
            c = Counter(name, description, labelnames=labelnames or [], registry=self.registry)
            self.metrics[name] = c
            log_info(f"MetricsManager: Registered Counter {name}.")
            return c

    def register_gauge(self, name: str, description: str, labelnames: Optional[list] = None):
        """
        Register a new Gauge metric.
        """
        with self._lock:
            g = Gauge(name, description, labelnames=labelnames or [], registry=self.registry)
            self.metrics[name] = g
            log_info(f"MetricsManager: Registered Gauge {name}.")
            return g

    def register_histogram(self, name: str, description: str, labelnames: Optional[list] = None):
        """
        Register a new Histogram metric.
        """
        with self._lock:
            h = Histogram(name, description, labelnames=labelnames or [], registry=self.registry)
            self.metrics[name] = h
            log_info(f"MetricsManager: Registered Histogram {name}.")
            return h

    def register_summary(self, name: str, description: str, labelnames: Optional[list] = None):
        """
        Register a new Summary metric.
        """
        with self._lock:
            s = Summary(name, description, labelnames=labelnames or [], registry=self.registry)
            self.metrics[name] = s
            log_info(f"MetricsManager: Registered Summary {name}.")
            return s

    def get_metric(self, name: str):
        """
        Get a registered metric by name.
        """
        return self.metrics.get(name)

    def scrape(self) -> bytes:
        """
        Generate the latest Prometheus metrics in text format.
        """
        return generate_latest(self.registry)
