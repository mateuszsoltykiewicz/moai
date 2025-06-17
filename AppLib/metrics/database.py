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
