from prometheus_client import Counter, Histogram

GRAFANA_OPERATIONS = Counter(
    "grafana_operations_total",
    "Total operations performed by Grafana client",
    ["operation", "status"]
)

GRAFANA_LATENCY = Histogram(
    "grafana_operation_latency_seconds",
    "Grafana operation latency",
    ["operation"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)
