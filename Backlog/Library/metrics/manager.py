"""
MetricsManager: Centralized Prometheus/OpenMetrics management.

- Registers and exposes metrics for all components
- Provides async lifecycle management
- Integrates with FastAPI for /metrics endpoint
- Supports custom metrics and labels
"""

from prometheus_client import (
    CollectorRegistry, Counter, Gauge, Histogram, Summary, generate_latest
)
from typing import Dict, Any, Optional
import asyncio
from .utils import log_info, log_error

class MetricsManager:
    def __init__(self):
        self.registry = CollectorRegistry()
        self.metrics: Dict[str, Any] = {}
        self._lock = asyncio.Lock()

    async def setup(self):
        log_info("MetricsManager: Setup complete.")

    async def shutdown(self):
        log_info("MetricsManager: Shutdown complete.")

    async def register_counter(self, name: str, description: str, labelnames: Optional[list] = None):
        async with self._lock:
            try:
                c = Counter(name, description, labelnames=labelnames or [], registry=self.registry)
                self.metrics[name] = c
                log_info(f"MetricsManager: Registered Counter {name}.")
                return c
            except Exception as e:
                log_error(f"Failed to register Counter {name}: {e}")
                raise

    async def register_gauge(self, name: str, description: str, labelnames: Optional[list] = None):
        async with self._lock:
            try:
                g = Gauge(name, description, labelnames=labelnames or [], registry=self.registry)
                self.metrics[name] = g
                log_info(f"MetricsManager: Registered Gauge {name}.")
                return g
            except Exception as e:
                log_error(f"Failed to register Gauge {name}: {e}")
                raise

    async def register_histogram(self, name: str, description: str, labelnames: Optional[list] = None):
        async with self._lock:
            try:
                h = Histogram(name, description, labelnames=labelnames or [], registry=self.registry)
                self.metrics[name] = h
                log_info(f"MetricsManager: Registered Histogram {name}.")
                return h
            except Exception as e:
                log_error(f"Failed to register Histogram {name}: {e}")
                raise

    async def register_summary(self, name: str, description: str, labelnames: Optional[list] = None):
        async with self._lock:
            try:
                s = Summary(name, description, labelnames=labelnames or [], registry=self.registry)
                self.metrics[name] = s
                log_info(f"MetricsManager: Registered Summary {name}.")
                return s
            except Exception as e:
                log_error(f"Failed to register Summary {name}: {e}")
                raise

    async def get_metric(self, name: str):
        async with self._lock:
            return self.metrics.get(name)

    def scrape(self) -> bytes:
        return generate_latest(self.registry)
