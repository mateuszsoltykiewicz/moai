from prometheus_client import Counter, Gauge

SESSION_OPERATIONS = Counter(
    "sessions_operations_total",
    "Total session operations",
    ["operation"]
)

ACTIVE_SESSIONS = Gauge(
    "sessions_active_count",
    "Current number of active sessions"
)

def record_session_operation(operation: str):
    SESSION_OPERATIONS.labels(operation=operation).inc()

def record_active_sessions(count: int):
    ACTIVE_SESSIONS.set(count)
