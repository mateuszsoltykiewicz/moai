from prometheus_client import Counter, Gauge

I2C_COMMANDS = Counter(
    "i2c_commands_total",
    "Total I2C commands executed",
    ["command"]
)

POWER_STATE = Gauge(
    "i2c_power_state",
    "Current power state (0=off, 1=on)"
)

def record_command(command: str):
    I2C_COMMANDS.labels(command=command).inc()
