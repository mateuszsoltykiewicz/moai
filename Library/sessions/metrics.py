from prometheus_client import Counter, Gauge, Histogram

SESSION_OPERATIONS = Counter(
    "sessions_operations_total",
    "Total session operations",
    ["operation"]
)

ACTIVE_SESSIONS = Gauge(
    "sessions_active_count",
    "Current number of active sessions"
)

SESSION_DURATION = Histogram(
    "session_duration_seconds",
    "Duration of sessions",
    buckets=[60, 300, 900, 3600, 86400]  # 1min, 5min, 15min, 1h, 1d
)

def record_session_operation(operation: str):
    SESSION_OPERATIONS.labels(operation=operation).inc()

def record_active_sessions(count: int):
    ACTIVE_SESSIONS.set(count)

def record_session_duration(duration: float):
    SESSION_DURATION.observe(duration)
