from prometheus_client import Counter, Gauge

# I2C Adapter Metrics
I2C_COMMANDS_TOTAL = Counter(
    "i2c_commands_total", "Total number of I2C commands processed", ["adapter_id"]
)
I2C_ERRORS_TOTAL = Counter(
    "i2c_errors_total", "Total I2C errors", ["adapter_id"]
)

# CANBus Adapter Metrics
CANBUS_MESSAGES_TOTAL = Counter(
    "canbus_messages_total", "Total CANBus messages processed", ["adapter_id"]
)
CANBUS_ERRORS_TOTAL = Counter(
    "canbus_errors_total", "Total CANBus errors", ["adapter_id"]
)
