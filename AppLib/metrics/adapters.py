from prometheus_client import Counter
from utils.prometheus_instrumentation import REGISTRY

I2C_COMMANDS_TOTAL = Counter(
    "i2c_commands_total",
    "Total number of I2C commands processed",
    ["adapter_id"],
    registry=REGISTRY
)
I2C_ERRORS_TOTAL = Counter(
    "i2c_errors_total",
    "Total I2C errors",
    ["adapter_id"],
    registry=REGISTRY
)
CANBUS_MESSAGES_TOTAL = Counter(
    "canbus_messages_total",
    "Total CANBus messages processed",
    ["adapter_id"],
    registry=REGISTRY
)
CANBUS_ERRORS_TOTAL = Counter(
    "canbus_errors_total",
    "Total CANBus errors",
    ["adapter_id"],
    registry=REGISTRY
)

def record_i2c_command(adapter_id: str):
    I2C_COMMANDS_TOTAL.labels(adapter_id=adapter_id).inc()

def record_i2c_error(adapter_id: str):
    I2C_ERRORS_TOTAL.labels(adapter_id=adapter_id).inc()

def record_canbus_message(adapter_id: str):
    CANBUS_MESSAGES_TOTAL.labels(adapter_id=adapter_id).inc()

def record_canbus_error(adapter_id: str):
    CANBUS_ERRORS_TOTAL.labels(adapter_id=adapter_id).inc()
