from prometheus_client import Counter

EXCEPTIONS_OCCURRED = Counter(
    "exceptions_occurred_total",
    "Total exceptions occurred",
    ["exception_type"]
)

def record_exception_occurred(exception_type: str):
    EXCEPTIONS_OCCURRED.labels(exception_type=exception_type).inc()
