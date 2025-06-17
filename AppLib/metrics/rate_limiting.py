from prometheus_client import Counter
from utils.prometheus_instrumentation import REGISTRY

RATE_LIMIT_ALLOWED = Counter(
    "rate_limit_allowed_total",
    "Total requests allowed by the rate limiter",
    ["scope"],
    registry=REGISTRY
)
RATE_LIMIT_BLOCKED = Counter(
    "rate_limit_blocked_total",
    "Total requests blocked by the rate limiter",
    ["scope"],
    registry=REGISTRY
)

def record_rate_limit_allowed(scope: str):
    RATE_LIMIT_ALLOWED.labels(scope=scope).inc()

def record_rate_limit_blocked(scope: str):
    RATE_LIMIT_BLOCKED.labels(scope=scope).inc()
