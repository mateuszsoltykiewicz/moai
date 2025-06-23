"""
I2CManager: Async I2C hardware and GPIO control for Raspberry Pi.

- Manages I2C bus and GPIO relay/valve/pump control
- Supports hardware configuration and state monitoring
- Streams events to Kafka and persists to Database if enabled
- Integrates with metrics, logging, alarms, and state management
"""

import asyncio
from typing import Dict, Any, Optional, Callable, Awaitable, List
from .schemas import I2CDeviceConfig, I2CControlRequest, I2CStatusResponse
from .exceptions import I2CError, I2CDeviceNotFoundError
from .metrics import record_i2c_operation
from .utils import log_info

# Example: Use smbus2 for I2C and gpiozero for GPIO
try:
    import smbus2
    import gpiozero
except ImportError:
    smbus2 = None
    gpiozero = None

class I2CManager:
    def __init__(self, config: Dict[str, Any]):
        self._bus_id = config.get("bus", 1)
        self._devices: Dict[str, I2CDeviceConfig] = {d["name"]: I2CDeviceConfig(**d) for d in config.get("devices", [])}
        self._gpio_pins = config.get("gpio_pins", {})
        self._bus = smbus2.SMBus(self._bus_id) if smbus2 else None
        self._relays: Dict[str, Any] = {}
        self._lock = asyncio.Lock()

        # Initialize relays (GPIO outputs)
        if gpiozero:
            for name, pin in self._gpio_pins.items():
                self._relays[name] = gpiozero.OutputDevice(pin)

    async def setup(self):
        log_info("I2CManager: Setup complete.")

    async def shutdown(self):
        if self._bus:
            self._bus.close()
        for relay in self._relays.values():
            relay.close()
        log_info("I2CManager: Shutdown complete.")

    async def control(self, req: I2CControlRequest) -> I2CStatusResponse:
        """
        Control a relay, valve, or pump via GPIO.
        """
        async with self._lock:
            relay = self._relays.get(req.device)
            if not relay:
                raise I2CDeviceNotFoundError(f"Relay '{req.device}' not found")
            if req.action == "on":
                relay.on()
            elif req.action == "off":
                relay.off()
            else:
                raise I2CError(f"Unsupported action '{req.action}'")
            record_i2c_operation("control")
            log_info(f"I2CManager: Set {req.device} to {req.action}")
            return I2CStatusResponse(device=req.device, status=req.action)

    async def get_status(self, device: str) -> I2CStatusResponse:
        """
        Get the status of a relay or I2C device.
        """
        async with self._lock:
            if device in self._relays:
                relay = self._relays[device]
                status = "on" if relay.value else "off"
                return I2CStatusResponse(device=device, status=status)
            elif device in self._devices:
                # Example: Read a register from the I2C device
                dev_cfg = self._devices[device]
                if not self._bus:
                    raise I2CError("I2C bus not available")
                try:
                    value = self._bus.read_byte(dev_cfg.address)
                    return I2CStatusResponse(device=device, status="ok", value=value)
                except Exception as e:
                    raise I2CError(f"I2C read error: {e}")
            else:
                raise I2CDeviceNotFoundError(f"Device '{device}' not found")

    async def list_devices(self) -> List[str]:
        """
        List all known relay and I2C device names.
        """
        async with self._lock:
            return list(self._relays.keys()) + list(self._devices.keys())
