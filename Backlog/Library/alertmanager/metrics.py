from prometheus_client import Counter, Histogram

ALERTMANAGER_OPERATIONS = Counter(
    "alertmanager_operations_total",
    "Total operations performed by AlertManager client",
    ["operation", "status"]
)

ALERTMANAGER_LATENCY = Histogram(
    "alertmanager_operation_latency_seconds",
    "AlertManager operation duration",
    ["operation"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)
