"""
Prometheus metrics for HealthManager.
"""

from prometheus_client import Counter, Histogram

HEALTH_CHECKS = Counter(
    "health_manager_checks_total",
    "Total health checks performed by HealthManager",
    ["status"]
)

HEALTH_CHECK_DURATION = Histogram(
    "health_manager_check_duration_seconds",
    "Duration of health checks by HealthManager",
    ["status"]
)

def record_health_check(status: str, duration: float = 0.0):
    HEALTH_CHECKS.labels(status=status).inc()
    if duration > 0:
        HEALTH_CHECK_DURATION.labels(status=status).observe(duration)
