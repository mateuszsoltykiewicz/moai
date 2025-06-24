from prometheus_client import Counter, Histogram, Gauge
from utils.prometheus_instrumentation import REGISTRY

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status_code"],
    registry=REGISTRY
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "Histogram of HTTP request durations",
    ["method", "endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.3, 1, 2.5, 5, 10],
    registry=REGISTRY
)
REQUESTS_IN_PROGRESS = Gauge(
    "http_requests_in_progress",
    "Number of HTTP requests in progress",
    ["endpoint"],
    registry=REGISTRY
)
CPU_USAGE = Gauge(
    "process_cpu_usage_percent",
    "CPU usage percent of the FastAPI process",
    registry=REGISTRY
)
MEMORY_USAGE = Gauge(
    "process_memory_usage_bytes",
    "Memory usage in bytes of the FastAPI process",
    registry=REGISTRY
)
ITEMS_CREATED = Counter(
    "items_created_total",
    "Total number of items created via the API",
    registry=REGISTRY
)

def record_http_request(method: str, endpoint: str, status_code: str):
    REQUEST_COUNT.labels(method=method, endpoint=endpoint, status_code=status_code).inc()

def observe_http_latency(method: str, endpoint: str, duration: float):
    REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(duration)
