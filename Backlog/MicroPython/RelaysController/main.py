import time
from machine import Pin
from lib.config_manager import load_config, log_event
from lib.relay_driver import RelayDriver
from lib.i2c_handler import I2CHandler
from lib.watchdog import Watchdog
from lib.rest_api import start_api
from lib.pins import RELAY_PINS, I2C_SDA, I2C_SCL, I2C_ADDR

def main():
    config = load_config()
    relay_driver = RelayDriver(RELAY_PINS, config["default_state"])
    i2c_handler = I2CHandler(
        relay_driver, config["command_map"],
        I2C_ADDR, Pin(I2C_SDA), Pin(I2C_SCL)
    )
    watchdog = Watchdog(timeout_ms=8000)
    start_api()
    log_event("SYSTEM_START", "RelaysController started")
    while True:
        i2c_handler.poll()
        watchdog.feed()
        time.sleep(0.01)

if __name__ == '__main__':
    main()
