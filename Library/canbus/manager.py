"""
CanbusManager: Async CANBus sensor streaming and configuration for Raspberry Pi.

- Manages CANBus interface and sensor configuration
- Streams sensor data (temperature, humidity, water level, gas, flame, etc.)
- Integrates with metrics, logging, alarms, and state management
"""

import asyncio
from typing import Dict, Any, Optional, Callable, Awaitable, List
from .schemas import CanbusSensorConfig, CanbusStreamResponse
from .exceptions import CanbusError, CanbusSensorNotFoundError
from .metrics import record_canbus_operation
from .utils import log_info

# Example: Use python-can for CANBus
try:
    import can
except ImportError:
    can = None

class CanbusManager:
    def __init__(self, config: Dict[str, Any]):
        self._interface = config.get("interface", "can0")
        self._baudrate = config.get("baudrate", 250000)
        self._sensors: Dict[str, CanbusSensorConfig] = {s["name"]: CanbusSensorConfig(**s) for s in config.get("sensors", [])}
        self._bus = can.interface.Bus(channel=self._interface, bustype='socketcan') if can else None
        self._lock = asyncio.Lock()

    async def setup(self):
        log_info("CanbusManager: Setup complete.")

    async def shutdown(self):
        if self._bus:
            self._bus.shutdown()
        log_info("CanbusManager: Shutdown complete.")

    async def stream_sensor(self, sensor_name: str, limit: int = 10) -> List[CanbusStreamResponse]:
        """
        Stream data for a configured sensor.
        """
        async with self._lock:
            if sensor_name not in self._sensors:
                raise CanbusSensorNotFoundError(f"Sensor '{sensor_name}' not found")
            sensor_cfg = self._sensors[sensor_name]
            if not self._bus:
                raise CanbusError("CANBus not available")
            messages = []
            try:
                for msg in self._bus:
                    if msg.arbitration_id == sensor_cfg.arbitration_id:
                        messages.append(
                            CanbusStreamResponse(
                                sensor=sensor_name,
                                arbitration_id=msg.arbitration_id,
                                data=list(msg.data),
                                timestamp=msg.timestamp
                            )
                        )
                        if len(messages) >= limit:
                            break
                record_canbus_operation("stream")
                log_info(f"CanbusManager: Streamed {len(messages)} messages for {sensor_name}")
            except Exception as e:
                raise CanbusError(f"CANBus stream error: {e}")
            return messages

    async def list_sensors(self) -> List[str]:
        """
        List all configured sensor names.
        """
        async with self._lock:
            return list(self._sensors.keys())
