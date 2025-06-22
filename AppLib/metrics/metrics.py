"""
CANBus Metrics for AppLib

- Prometheus metrics for CANBus operations
- Used by /api/routers/canbus.py
"""

from prometheus_client import Counter, Histogram

CANBUS_OPERATIONS = Counter(
    "canbus_operations_total",
    "Total CANBus operations by type",
    ["operation"]
)

CANBUS_OPERATION_DURATION = Histogram(
    "canbus_operation_duration_seconds",
    "Duration of CANBus operations by type",
    ["operation"]
)

CANBUS_MESSAGES_STREAMED = Counter(
    "canbus_messages_streamed_total",
    "Total CANBus messages streamed",
    ["adapter_id"]
)

def record_canbus_operation(operation: str, duration: float, count: int = 0, adapter_id: str = None):
    """
    Record metrics for a CANBus operation.

    Args:
        operation: Operation name (e.g., "configure", "get_status", "stream")
        duration: Operation duration in seconds
        count: Number of messages streamed (for "stream" operation)
        adapter_id: Adapter ID (for message streaming)
    """
    CANBUS_OPERATIONS.labels(operation=operation).inc()
    CANBUS_OPERATION_DURATION.labels(operation=operation).observe(duration)
    if operation == "stream" and count and adapter_id:
        CANBUS_MESSAGES_STREAMED.labels(adapter_id=adapter_id).inc(count)
