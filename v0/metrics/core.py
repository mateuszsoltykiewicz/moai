"""
Endpoint metrics recording
"""

from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP Requests",
    ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["method", "endpoint"]
)

def record_endpoint_metrics(path: str, method: str, status_code: int, duration: float):
    """Record metrics for an endpoint"""
    REQUEST_COUNT.labels(method=method, endpoint=path, status=status_code).inc()
    REQUEST_LATENCY.labels(method=method, endpoint=path).observe(duration)


# Health checks
HEALTH_CHECKS = Counter(
    "health_checks_total",
    "Total health checks",
    ["status"]
)

# Alarm operations
ALARM_OPERATIONS = Counter(
    "alarm_operations_total",
    "Total alarm operations",
    ["operation"]
)
ALARM_DURATION = Histogram(
    "alarm_operation_duration_seconds",
    "Duration of alarm operations",
    ["operation"]
)

def record_health_check(status: str, duration: float):
    HEALTH_CHECKS.labels(status=status).inc()
    # Additional metrics as needed

def record_alarm_operation(operation: str, duration: float, count: int = 0):
    ALARM_OPERATIONS.labels(operation=operation).inc()
    ALARM_DURATION.labels(operation=operation).observe(duration)
    # Additional metrics as needed
