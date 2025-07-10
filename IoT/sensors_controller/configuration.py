import machine
from utime import time
import machine
from IoT.iotlib.configuration import Configuration


TEMPERATURE_SENSOR_PIN=1
WATER_AVAILABLE_PIN=2
FLAME_DETECTOR_PIN=3
GAS_DETECTOR_PIN=4

# --- Extended Configuration for Relays and Metrics ---
class RelaysConfiguration(Configuration):
    """
    Extends Configuration with hardware and metrics attributes.
    """
    def __init__(self, app, wlan):
        super().__init__(app=app, wlan=wlan)

        self.temperature_sensor_pin = machine.Pin(TEMPERATURE_SENSOR_PIN, machine.Pin.IN)
        self.water_available_pin = machine.Pin(WATER_AVAILABLE_PIN, machine.Pin.IN)
        self.flame_detector_pin = machine.Pin(FLAME_DETECTOR_PIN, machine.Pin.IN)
        self.gas_detector_pin = machine.Pin(GAS_DETECTOR_PIN, machine.Pin.IN)

        self.current_temperature = 0.0
        self.last_temperature = 0.0

        self.metrics_last_request = time()

        self.water_available = False
        self.gas_leak = False

        self.water_available = False