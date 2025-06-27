# canbus/manager.py
"""
Production-grade CanbusManager with async streaming, buffering, and error recovery.
"""

import asyncio
from typing import Dict, Any, List, Tuple
from collections import deque
from .schemas import CanbusSensorConfig, CanbusStreamResponse
from .exceptions import CanbusError, CanbusSensorNotFoundError
from .metrics import record_canbus_operation
from .utils import log_info, log_error

try:
    import can
    from can import Message
except ImportError:
    can = None

class CanbusManager:
    def __init__(self, config: Dict[str, Any]):
        self._interface = config.get("interface", "can0")
        self._baudrate = config.get("baudrate", 250000)
        self._sensors: Dict[str, CanbusSensorConfig] = {}
        self._bus = None
        self._lock = asyncio.Lock()
        self._running = False
        self._message_queue = asyncio.Queue(maxsize=1000)
        self._consumer_task = None
        self._producer_task = None
        
        # Load sensor configurations
        for sensor_cfg in config.get("sensors", []):
            sensor = CanbusSensorConfig(**sensor_cfg)
            self._sensors[sensor.name] = sensor

    async def setup(self):
        """Initialize CAN bus and start background tasks"""
        if can is None:
            raise CanbusError("python-can not installed")
        
        try:
            self._bus = can.interface.Bus(
                channel=self._interface,
                bustype='socketcan',
                bitrate=self._baudrate
            )
            self._running = True
            self._producer_task = asyncio.create_task(self._message_producer())
            self._consumer_task = asyncio.create_task(self._message_consumer())
            log_info("CanbusManager: Setup complete")
        except Exception as e:
            log_error(f"CANBus initialization failed: {e}")
            raise CanbusError(f"CANBus init error: {e}")

    async def shutdown(self):
        """Graceful shutdown"""
        self._running = False
        if self._producer_task:
            self._producer_task.cancel()
        if self._consumer_task:
            self._consumer_task.cancel()
        if self._bus:
            self._bus.shutdown()
        log_info("CanbusManager: Shutdown complete")

    async def _message_producer(self):
        """Read CAN messages and put in queue"""
        while self._running:
            try:
                msg = self._bus.recv(timeout=0.1)  # Non-blocking read
                if msg:
                    await self._message_queue.put(msg)
            except Exception as e:
                log_error(f"CANBus read error: {e}")
                await asyncio.sleep(1)  # Backoff on error

    async def _message_consumer(self):
        """Process messages from queue"""
        while self._running:
            try:
                msg: Message = await self._message_queue.get()
                # Here you'd normally process and route messages
                # For now we just log
                log_info(f"Received CAN message: {msg.arbitration_id}")
            except Exception as e:
                log_error(f"Message processing error: {e}")

    async def stream_sensor(self, sensor_name: str, limit: int = 10) -> List[CanbusStreamResponse]:
        """Get recent messages for a sensor"""
        async with self._lock:
            if sensor_name not in self._sensors:
                raise CanbusSensorNotFoundError(f"Sensor '{sensor_name}' not found")
            
            sensor_cfg = self._sensors[sensor_name]
            results = []
            
            # This would come from a sensor-specific buffer in real implementation
            for _ in range(min(limit, self._message_queue.qsize())):
                msg = self._message_queue.get_nowait()
                if msg.arbitration_id == sensor_cfg.arbitration_id:
                    results.append(CanbusStreamResponse(
                        sensor=sensor_name,
                        arbitration_id=msg.arbitration_id,
                        data=list(msg.data),
                        timestamp=msg.timestamp
                    ))
            
            record_canbus_operation("stream")
            return results

    async def list_sensors(self) -> List[str]:
        return list(self._sensors.keys())
