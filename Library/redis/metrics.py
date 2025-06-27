from prometheus_client import Counter, Histogram

REDIS_OPERATIONS = Counter(
    "redis_manager_operations_total",
    "Total operations performed by RedisManager",
    ["operation", "status"]
)

REDIS_LATENCY = Histogram(
    "redis_manager_operation_latency_seconds",
    "Redis operation latency",
    ["operation"],
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0]
)

def record_redis_operation(operation: str, status: str = "success"):
    REDIS_OPERATIONS.labels(operation=operation, status=status).inc()

def record_redis_latency(operation: str, latency: float):
    REDIS_LATENCY.labels(operation=operation).observe(latency)
