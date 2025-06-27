import asyncio
from typing import Dict, Any, List
from .schemas import I2CDeviceConfig, I2CControlRequest, I2CStatusResponse
from .exceptions import I2CError, I2CDeviceNotFoundError, I2CInvalidActionError
from .metrics import record_i2c_operation
from .utils import log_info, log_error

try:
    import smbus2
    import gpiozero
except ImportError:
    smbus2 = None
    gpiozero = None

class I2CManager:
    def __init__(self, config: Dict[str, Any]):
        self._bus_id = config.get("bus", 1)
        self._devices: Dict[str, I2CDeviceConfig] = {}
        self._gpio_pins = config.get("gpio_pins", {})
        self._bus = None
        self._relays: Dict[str, gpiozero.OutputDevice] = {}
        self._lock = asyncio.Lock()
        self._device_states: Dict[str, str] = {}  # Track device states
        
        # Load device configurations
        for device_cfg in config.get("devices", []):
            device = I2CDeviceConfig(**device_cfg)
            self._devices[device.name] = device
            self._device_states[device.name] = "unknown"
        
        # Initialize relays with safe defaults
        for name, pin in self._gpio_pins.items():
            self._relays[name] = gpiozero.OutputDevice(pin, active_high=False)
            self._device_states[name] = "off"

    async def setup(self):
        if smbus2:
            self._bus = smbus2.SMBus(self._bus_id)
        log_info("I2CManager: Setup complete")

    async def shutdown(self):
        # Safe shutdown: Turn off all relays
        for name in self._relays:
            await self._safe_control(name, "off")
        
        if self._bus:
            self._bus.close()
        log_info("I2CManager: Shutdown complete")

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
            log_info(f"Device {device} already in state {action}")
            return
        
        try:
            if action == "on":
                await self._run_in_executor(relay.on)
            else:
                await self._run_in_executor(relay.off)
                
            self._device_states[device] = action
            log_info(f"Set {device} to {action}")
        except Exception as e:
            log_error(f"Hardware control failed for {device}: {str(e)}")
            raise I2CError(f"Control failed: {str(e)}")

    async def control(self, req: I2CControlRequest) -> I2CStatusResponse:
        async with self._lock:
            await self._safe_control(req.device, req.action)
            record_i2c_operation("control")
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
                    log_error(f"I2C read error for {device}: {str(e)}")
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
                    log_error(f"Watchdog: Device {device} failed")
                    # Trigger recovery
            await asyncio.sleep(10)
