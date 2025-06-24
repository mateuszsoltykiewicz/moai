from prometheus_client import Counter, Histogram

HEALTH_CHECKS_TOTAL = Counter(
    "health_checks_total",
    "Total health checks by status",
    ["probe", "status"]
)
HEALTH_CHECK_DURATION = Histogram(
    "health_check_duration_seconds",
    "Duration of health checks by probe",
    ["probe"]
)

def record_health_check(probe: str, status: str, duration: float):
    HEALTH_CHECKS_TOTAL.labels(probe=probe, status=status).inc()
    HEALTH_CHECK_DURATION.labels(probe=probe).observe(duration)
