"""
Prometheus metrics for CanbusManager.
"""

from prometheus_client import Counter

CANBUS_OPERATIONS = Counter(
    "canbus_manager_operations_total",
    "Total operations performed by CanbusManager",
    ["operation"]
)

CANBUS_MESSAGE_COUNT = Counter(
    "canbus_messages_total",
    "Total CAN messages received",
    ["arbitration_id"]
)

def record_canbus_operation(operation: str):
    CANBUS_OPERATIONS.labels(operation=operation).inc()

def record_canbus_message(msg: str):
    CANBUS_MESSAGE_COUNT.labels(arbitration_id=msg.arbitration_id).inc()