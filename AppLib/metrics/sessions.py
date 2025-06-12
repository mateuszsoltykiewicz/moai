# HTTP request metrics (for API endpoints)
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status_code"]
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "Histogram of HTTP request durations",
    ["method", "endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.3, 1, 2.5, 5, 10]
)

REQUESTS_IN_PROGRESS = Gauge(
    "http_requests_in_progress",
    "Number of HTTP requests in progress",
    ["endpoint"]
)

# System-level metrics
CPU_USAGE = Gauge(
    "process_cpu_usage_percent",
    "CPU usage percent of the FastAPI process"
)

MEMORY_USAGE = Gauge(
    "process_memory_usage_bytes",
    "Memory usage in bytes of the FastAPI process"
)

# Example business/domain metric
ITEMS_CREATED = Counter(
    "items_created_total",
    "Total number of items created via the API"
)