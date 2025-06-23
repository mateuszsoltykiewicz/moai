"""
Reusable metric definitions for other components.
"""

from prometheus_client import Counter, Histogram

# Example: General operation counter
GENERAL_OPERATIONS = Counter(
    "general_operations_total",
    "Total operations across all components",
    ["component", "operation"]
)

# Example: General operation duration
GENERAL_OPERATION_DURATION = Histogram(
    "general_operation_duration_seconds",
    "Duration of operations across all components",
    ["component", "operation"]
)

def record_general_operation(component: str, operation: str, duration: float = None):
    GENERAL_OPERATIONS.labels(component=component, operation=operation).inc()
    if duration is not None:
        GENERAL_OPERATION_DURATION.labels(component=component, operation=operation).observe(duration)
