"""
I2C Bus Session Manager

- Manages I2C bus resource acquisition and cleanup.
- Context manager interface for safe open/close of the bus.
- Optionally supports async use via thread executor for non-blocking I/O.
- Compatible with smbus2 and similar libraries.
"""

from smbus2 import SMBus
from typing import Optional
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor

class I2CBusManager:
    def __init__(self, bus_id: int = 1):
        self.bus_id = bus_id
        self.bus: Optional[SMBus] = None
        self.logger = logging.getLogger("I2CBusManager")
        self._executor = ThreadPoolExecutor(max_workers=1)

    def __enter__(self) -> SMBus:
        try:
            self.bus = SMBus(self.bus_id)
            self.logger.info(f"I2C bus {self.bus_id} opened.")
            return self.bus
        except Exception as exc:
            self.logger.error(f"Failed to open I2C bus {self.bus_id}: {exc}")
            raise

    def __exit__(self, exc_type, exc, tb):
        if self.bus:
            try:
                self.bus.close()
                self.logger.info(f"I2C bus {self.bus_id} closed.")
            except Exception as exc:
                self.logger.warning(f"Error closing I2C bus {self.bus_id}: {exc}")

    async def async_read_byte(self, addr: int) -> int:
        """
        Asynchronously read a byte from the given device address.
        """
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self._executor, self.bus.read_byte, addr)

    async def async_write_byte(self, addr: int, value: int):
        """
        Asynchronously write a byte to the given device address.
        """
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self._executor, self.bus.write_byte, addr, value)
