import asyncio
from typing import Dict, Any, List
from .schemas import I2CDeviceConfig, I2CControlRequest, I2CStatusResponse
from .exceptions import I2CError, I2CDeviceNotFoundError, I2CInvalidActionError
from .metrics import record_i2c_operation
from Library.logging import get_logger

try:
    import smbus2
    import gpiozero
except ImportError:
    smbus2 = None
    gpiozero = None

logger = get_logger(__name__)

class I2CManager:
    def __init__(self, config: Dict[str, Any]):
        self._bus_id = config.get("bus", 1)
        self._devices: Dict[str, I2CDeviceConfig] = {}
        self._gpio_pins = config.get("gpio_pins", {})
        self._bus = None
        self._relays: Dict[str, gpiozero.OutputDevice] = {}
        self._lock = asyncio.Lock()
        self._device_states: Dict[str, str] = {}
        
        # Load device configurations
        for device_cfg in config.get("devices", []):
            device = I2CDeviceConfig(**device_cfg)
            self._devices[device.name] = device
            self._device_states[device.name] = "unknown"
        
        # Initialize relays
        for name, pin in self._gpio_pins.items():
            self._relays[name] = gpiozero.OutputDevice(pin, active_high=False)
            self._device_states[name] = "off"

    async def setup(self):
        if smbus2:
            self._bus = smbus2.SMBus(self._bus_id)
        logger.info("I2C setup complete")

    async def shutdown(self):
        # Safe shutdown: Turn off all relays
        for name in self._relays:
            await self._safe_control(name, "off")
        
        if self._bus:
            self._bus.close()
        logger.info("I2C shutdown complete")

    async def _run_in_executor(self, func, *args):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, func, *args)

    async def _safe_control(self, device: str, action: str):
        """Thread-safe hardware control with validation"""
        if device not in self._relays:
            raise I2CDeviceNotFoundError(f"Device '{device}' not found")
        
        if action not in ["on", "off"]:
            raise I2CInvalidActionError(f"Invalid action '{action}'")
        
        relay = self._relays[device]
        current_state = self._device_states[device]
        
        # Prevent redundant operations
        if (action == "on" and current_state == "on") or \
           (action == "off" and current_state == "off"):
            logger.info(f"Device {device} already in state {action}")
            return
        
        try:
            if action == "on":
                await self._run_in_executor(relay.on)
            else:
                await self._run_in_executor(relay.off)
                
            self._device_states[device] = action
            logger.info(f"Set {device} to {action}")
        except Exception as e:
            logger.error(f"Hardware control failed for {device}: {str(e)}", exc_info=True)
            raise I2CError(f"Control failed: {str(e)}")

    async def control(self, req: I2CControlRequest) -> I2CStatusResponse:
        async with self._lock:
            await self._safe_control(req.device, req.action)
            record_i2c_operation("control", req.device)
            return I2CStatusResponse(device=req.device, status=self._device_states[req.device])

    async def get_status(self, device: str) -> I2CStatusResponse:
        async with self._lock:
            if device in self._device_states:
                return I2CStatusResponse(
                    device=device,
                    status=self._device_states[device]
                )
            elif device in self._devices:
                # I2C device status check
                dev_cfg = self._devices[device]
                try:
                    value = await self._run_in_executor(
                        self._bus.read_byte, 
                        dev_cfg.address
                    )
                    return I2CStatusResponse(
                        device=device,
                        status="active",
                        value=value
                    )
                except Exception as e:
                    logger.error(f"I2C read error for {device}: {str(e)}", exc_info=True)
                    raise I2CError(f"Read failed: {str(e)}")
            raise I2CDeviceNotFoundError(f"Device '{device}' not found")

    async def list_devices(self) -> List[str]:
        return list(self._device_states.keys())

    async def _watchdog(self):
        while True:
            for device in self._device_states:
                try:
                    await self.get_status(device)
                except I2CError:
                    logger.error(f"Watchdog: Device {device} failed", exc_info=True)
                    # Trigger recovery
            await asyncio.sleep(10)
