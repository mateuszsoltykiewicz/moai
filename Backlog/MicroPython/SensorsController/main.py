import time
from lib.config_manager import load_config, log_event
from lib.pins import *
from lib.sensor_drivers.dht11 import DHT11
from lib.sensor_drivers.flame import FlameSensor
from lib.sensor_drivers.gas import GasSensor
from lib.sensor_drivers.liquid_level import LiquidLevelSensor
from lib.sensor_drivers.water_temp import WaterTempSensor
from lib.sensor_drivers.flow import FlowSensor
from lib.canbus_handler import CANBusHandler
from lib.rest_api import start_api
from lib.watchdog import Watchdog

def main():
    config = load_config()
    dht11 = DHT11(DHT11_PIN)
    flame = FlameSensor(FLAME_PIN)
    gas = GasSensor(GAS_PIN)
    liquid_level = LiquidLevelSensor(LIQUID_LEVEL_PIN)
    water_temp = WaterTempSensor(WATER_TEMP_PIN)
    flow = FlowSensor(FLOW_PIN)
    canbus_handler = CANBusHandler(config)
    watchdog = Watchdog(timeout_ms=8000)
    start_api()
    log_event("SYSTEM_START", "SensorsController started")
    while True:
        canbus_handler.poll()
        if canbus_handler.streaming_enabled:
            data = {
                "dht11": dht11.read(),
                "flame": flame.read(),
                "gas": gas.read(),
                "liquid_level": liquid_level.read(),
                "water_temp": water_temp.read(),
                "flow": flow.read()
            }
            canbus_handler.send_sensor_data(data)
        watchdog.feed()
        time.sleep(0.5)

if __name__ == '__main__':
    main()
