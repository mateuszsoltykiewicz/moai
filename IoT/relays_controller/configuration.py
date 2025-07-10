import machine
from utime import time
from IoT.iotlib.configuration import Configuration

# --- Hardware Pin Definitions ---
PUMP_PIN = 18
GAS_VALVE_PIN = 19
SPARK_PIN = 20
SHOWER_PIN = 21

# --- Extended Configuration for Relays and Metrics ---
class RelaysConfiguration(Configuration):
    """
    Extends Configuration with hardware and metrics attributes.
    """
    def __init__(self, app, wlan, metrics_poll_url,
                 target_temp=38, delta_temp_timeout=180, expectec_delta_temp=1.0,
                 metrics_poll_interval=1, metrics_poll_timeout=2):
        super().__init__(app=app, wlan=wlan)
        self.is_heating = False
        self.heating_engaged = False
        self.target_temp = target_temp
        self.pump = machine.Pin(PUMP_PIN, machine.Pin.OUT, value=0)
        self.gas_valve = machine.Pin(GAS_VALVE_PIN, machine.Pin.OUT, value=0)
        self.spark = machine.Pin(SPARK_PIN, machine.Pin.OUT, value=0)
        self.shower = machine.Pin(SHOWER_PIN, machine.Pin.OUT, value=0)
        self.delta_temp_timeout = delta_temp_timeout
        self.current_temperature = 0.0
        self.last_temperature = 0.0
        self.expected_delta_temp = expectec_delta_temp
        self.metrics_poll_interval = metrics_poll_interval
        self.metrics_poll_timeout = metrics_poll_timeout
        self.metrics_poll_url = metrics_poll_url
        self.metrics_last_update = time()  # Ensure initialized to avoid TypeError
        self.water_available = True
        self.gas_leak = False  # Use consistent naming