"""
Enhanced metrics with per-check tracking and duration histograms.
"""

from prometheus_client import Counter, Histogram

HEALTH_CHECKS = Counter(
    "health_checks_total",
    "Total health checks performed",
    ["check_name", "status"]
)

HEALTH_CHECK_DURATION = Histogram(
    "health_check_duration_seconds",
    "Duration of health checks",
    ["check_name"],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0]
)

def record_health_check(check_name: str, status: str):
    HEALTH_CHECKS.labels(check_name=check_name, status=status).inc()

def record_health_check_duration(check_name: str, duration: float):
    HEALTH_CHECK_DURATION.labels(check_name=check_name).observe(duration)
