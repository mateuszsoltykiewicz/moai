from prometheus_client import Counter

EXCEPTIONS_TOTAL = Counter(
    "exceptions_total",
    "Total exceptions received",
    ["service", "status"]
)

def record_exception(service: str, status: str):
    EXCEPTIONS_TOTAL.labels(service=service, status=status).inc()
