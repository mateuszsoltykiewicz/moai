from prometheus_client import Counter
from utils.prometheus_instrumentation import REGISTRY

DB_QUERIES_TOTAL = Counter(
    "db_queries_total",
    "Total number of database queries",
    ["operation"],
    registry=REGISTRY
)
DB_ERRORS_TOTAL = Counter(
    "db_errors_total",
    "Total database errors",
    ["operation"],
    registry=REGISTRY
)

def record_db_query(operation: str):
    DB_QUERIES_TOTAL.labels(operation=operation).inc()

def record_db_error(operation: str):
    DB_ERRORS_TOTAL.labels(operation=operation).inc()

DATABASE_OPERATIONS = Counter(
    "database_operations_total",
    "Total database operations by type",
    ["operation"]
)

DATABASE_OPERATION_DURATION = Histogram(
    "database_operation_duration_seconds",
    "Duration of database operations by type",
    ["operation"]
)

def record_database_operation(operation: str, duration: float, count: int = 0):
    DATABASE_OPERATIONS.labels(operation=operation).inc()
    DATABASE_OPERATION_DURATION.labels(operation=operation).observe(duration)
    if count > 0:
        # Additional metric for list operations
        DATABASE_OPERATIONS.labels(operation=f"{operation}_items").inc(count)
