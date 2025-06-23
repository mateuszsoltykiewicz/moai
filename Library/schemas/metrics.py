"""
Prometheus metrics for SchemasManager.
"""

from prometheus_client import Counter

SCHEMA_OPERATIONS = Counter(
    "schemas_manager_operations_total",
    "Total operations performed by SchemasManager",
    ["operation"]
)

def record_schema_operation(operation: str):
    SCHEMA_OPERATIONS.labels(operation=operation).inc()
