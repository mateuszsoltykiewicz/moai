from machine import I2C
from lib.i2c_slave import I2CSlave  # From rp2040-i2c-slave project
from lib.config_manager import log_event

class I2CHandler:
    def __init__(self, relay_driver, command_map, i2c_addr, sda, scl):
        self.i2c = I2C(0, scl=scl, sda=sda, freq=100_000)
        self.slave = I2CSlave(self.i2c, addr=i2c_addr)
        self.relay_driver = relay_driver
        self.command_map = command_map

    def poll(self):
        data = self.slave.read(64)
        if data:
            try:
                cmd = data.decode().strip()
                resp = self.relay_driver.handle_command(cmd, self.command_map)
                self.slave.write(resp)
                log_event("I2C_CMD", f"Received: {cmd}, Responded: {resp}")
            except Exception as e:
                log_event("I2C_ERROR", str(e))
                self.slave.write(b"ERR")
