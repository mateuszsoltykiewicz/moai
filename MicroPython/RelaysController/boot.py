from lib.config_manager import load_config
from lib.relay_driver import RelayDriver
from lib.pins import RELAY_PINS

def boot():
    config = load_config()
    relay_driver = RelayDriver(RELAY_PINS, config["default_state"])
    relay_driver.safe_state()

boot()
