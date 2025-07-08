from prometheus_client import Counter

REDIS_OPERATIONS = Counter(
    "redis_operations_total",
    "Total operations performed by RedisManager",
    ["operation", "status"]
)

def record_redis_operation(operation: str, status: str = "success"):
    REDIS_OPERATIONS.labels(operation=operation, status=status).inc()
