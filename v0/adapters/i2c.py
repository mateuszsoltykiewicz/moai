# adapters/i2c.py
import asyncio
from contextlib import asynccontextmanager
from typing import Dict, Any, List, AsyncIterator, Optional
import aioi2c  # Async I2C library
from aioi2c import I2CError, I2CDevice

from core.exceptions import I2CException
from core.logging import get_logger
from metrics.adapters import (
    I2C_COMMANDS_SENT,
    I2C_ERRORS,
    I2C_HEALTH_CHECKS,
    I2C_HEALTH_CHECK_FAILS
)

logger = get_logger(__name__)

class I2CProtocol(ABC):
    """Abstract base class for protocol-specific command encoding"""
    @abstractmethod
    def encode_command(self, command: Dict[str, Any]) -> bytes:
        raise NotImplementedError
    
    @abstractmethod
    def decode_response(self, raw_data: bytes) -> Dict[str, Any]:
        raise NotImplementedError

class DefaultI2CProtocol(I2CProtocol):
    """Default pass-through protocol implementation"""
    def encode_command(self, command: Dict[str, Any]) -> bytes:
        return bytes(command.get("data", []))
    
    def decode_response(self, raw_data: bytes) -> Dict[str, Any]:
        return {"raw": list(raw_data)}

class I2CAdapter:
    def __init__(
        self,
        adapter_id: str,
        bus_number: int = 1,
        device_address: int = 0x00,
        protocol: Type[I2CProtocol] = DefaultI2CProtocol,
        retries: int = 3,
        retry_delay: float = 0.1
    ):
        self.adapter_id = adapter_id
        self.bus_number = bus_number
        self.device_address = device_address
        self.protocol = protocol()
        self.retries = retries
        self.retry_delay = retry_delay
        
        self._device: Optional[I2CDevice] = None
        self._lock = asyncio.Lock()
        self._monitor_task: Optional[asyncio.Task] = None
        self._monitor_running = False
        self._healthy = False

    @asynccontextmanager
    async def context(self) -> AsyncIterator['I2CAdapter']:
        """Async context manager for safe connection handling"""
        try:
            await self.connect()
            await self.start_monitoring()
            yield self
        finally:
            await self.disconnect()

    async def connect(self) -> None:
        """Establish connection to I2C device"""
        async with self._lock:
            if self._device and self._device.connected:
                return

            try:
                self._device = await aioi2c.connect(
                    bus=self.bus_number,
                    address=self.device_address
                )
                self._healthy = True
                logger.info(
                    f"I2C {self.adapter_id} connected",
                    extra={"bus": self.bus_number, "address": hex(self.device_address)}
                )
            except I2CError as e:
                self._healthy = False
                await self._handle_error("Connection failed", e)
                raise I2CException(f"Connection error: {str(e)}") from e

    async def disconnect(self) -> None:
        """Close connection gracefully"""
        async with self._lock:
            self._monitor_running = False
            if self._monitor_task:
                self._monitor_task.cancel()
                try:
                    await self._monitor_task
                except asyncio.CancelledError:
                    pass

            if self._device and self._device.connected:
                try:
                    await self._device.disconnect()
                    logger.info(f"I2C {self.adapter_id} disconnected")
                except I2CError as e:
                    await self._handle_error("Disconnect failed", e)
                finally:
                    self._device = None
                    self._healthy = False

    #region Command Execution
    async def execute_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single command with retries and protocol encoding"""
        for attempt in range(1, self.retries + 1):
            try:
                if not self._device or not self._device.connected:
                    await self.connect()

                encoded = self.protocol.encode_command(command)
                response = await self._device.write_read(encoded, read_length=command.get("read_length", 0))
                decoded = self.protocol.decode_response(response)
                
                I2C_COMMANDS_SENT.labels(adapter_id=self.adapter_id).inc()
                return decoded
            except I2CError as e:
                if attempt == self.retries:
                    await self._handle_error("Command failed after retries", e)
                    raise I2CException(f"Command failed: {str(e)}") from e
                
                await self._handle_error(f"Command failed (attempt {attempt})", e)
                await asyncio.sleep(self.retry_delay)
                await self._reconnect()

    async def queue_commands(self, commands: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute multiple commands in sequence"""
        results = []
        for cmd in commands:
            results.append(await self.execute_command(cmd))
        return results
    #endregion

    #region Health Monitoring
    async def health_check(self) -> bool:
        """Verify device responsiveness"""
        try:
            if not self._device or not self._device.connected:
                return False

            # Send NULL command and check response
            response = await self._device.write_read(b'\x00', read_length=1)
            self._healthy = len(response) == 1
            I2C_HEALTH_CHECKS.labels(adapter_id=self.adapter_id).inc()
            return self._healthy
        except I2CError as e:
            I2C_HEALTH_CHECK_FAILS.labels(adapter_id=self.adapter_id).inc()
            await self._handle_error("Health check failed", e)
            self._healthy = False
            return False

    async def start_monitoring(self, interval: float = 10.0):
        """Start background health monitoring"""
        self._monitor_running = True
        self._monitor_task = asyncio.create_task(
            self._monitor_loop(interval)
        )

    async def _monitor_loop(self, interval: float):
        while self._monitor_running:
            healthy = await self.health_check()
            if not healthy:
                logger.warning("I2C unhealthy, attempting reconnection")
                try:
                    await self._reconnect()
                except I2CException as e:
                    logger.error(f"Reconnection failed: {e}")
            await asyncio.sleep(interval)

    async def _reconnect(self):
        """Reconnect with exponential backoff"""
        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                await self.disconnect()
                await self.connect()
                logger.info(f"Reconnected to I2C after {attempt} attempts")
                return
            except I2CError as e:
                delay = 2 ** attempt
                await self._handle_error(f"Reconnect attempt {attempt} failed", e)
                await asyncio.sleep(delay)
        
        raise I2CException("Failed to reconnect after multiple attempts")
    #endregion

    #region GPIO Management
    async def configure_gpio(self, pin: int, mode: str, pullup: Optional[bool] = None):
        """Configure GPIO pin mode (if supported by device)"""
        try:
            await self._device.write(f"CONFIG_GPIO {pin} {mode} {pullup}".encode())
            logger.debug("GPIO configured", extra={"pin": pin, "mode": mode})
        except I2CError as e:
            await self._handle_error("GPIO config failed", e)
            raise I2CException(f"GPIO configuration error: {str(e)}") from e
    #endregion

    #region Error Handling
    async def _handle_error(self, context: str, error: Exception) -> None:
        """Centralized error logging and metrics"""
        I2C_ERRORS.labels(adapter_id=self.adapter_id).inc()
        logger.error(
            f"{context}: {str(error)}",
            exc_info=error,
            extra={
                "adapter": self.adapter_id,
                "bus": self.bus_number,
                "address": hex(self.device_address)
            }
        )
    #endregion
