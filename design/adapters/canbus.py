# adapters/canbus.py
import asyncio
from contextlib import asynccontextmanager
from typing import Optional, List, Dict, Any, AsyncIterator, Type
import can
from can import Bus, AsyncBufferedReader, Notifier, Message
from can.exceptions import CanError, CanOperationError
from abc import ABC, abstractmethod

from exceptions.canbus import CANBusException
from core.logging import get_logger
from metrics.adapters import (
    CANBUS_MESSAGES_READ,
    CANBUS_MESSAGES_WRITTEN,
    CANBUS_ERRORS,
    CANBUS_WRITE_ERRORS,
    CANBUS_HEALTH_CHECKS,
    CANBUS_HEALTH_CHECK_FAILS
)

logger = get_logger(__name__)

class CANBusProtocol(ABC):
    """Abstract base class for protocol-specific encoding/decoding"""
    @abstractmethod
    def encode(self, data: Dict[str, Any]) -> bytes:
        raise NotImplementedError
    
    @abstractmethod
    def decode(self, raw_data: bytes) -> Dict[str, Any]:
        raise NotImplementedError

class DefaultProtocol(CANBusProtocol):
    """Default pass-through protocol implementation"""
    def encode(self, data: Dict[str, Any]) -> bytes:
        return bytes(data.get("payload", []))
    
    def decode(self, raw_data: bytes) -> Dict[str, Any]:
        return {"raw": list(raw_data)}

class CANBusAdapter:
    def __init__(
        self, 
        channel: str,
        bitrate: int,
        interface: str = "socketcan",
        can_filters: Optional[List[Dict[str, Any]]] = None,
        protocol: Type[CANBusProtocol] = DefaultProtocol
    ):
        self.channel = channel
        self.bitrate = bitrate
        self.interface = interface
        self.can_filters = can_filters
        self.protocol = protocol()
        
        self._bus: Optional[Bus] = None
        self._reader: Optional[AsyncBufferedReader] = None
        self._notifier: Optional[Notifier] = None
        self._is_configured = False
        self._shutdown_lock = asyncio.Lock()
        self._monitor_task: Optional[asyncio.Task] = None
        self._monitor_running = False

    @asynccontextmanager
    async def context(self) -> AsyncIterator['CANBusAdapter']:
        """Async context manager with automatic monitoring"""
        try:
            await self.configure()
            await self.start_monitoring()
            yield self
        finally:
            await self.stop()

    async def configure(self) -> None:
        """Configure and start CAN bus interface"""
        if self._is_configured:
            return

        try:
            self._bus = Bus(
                interface=self.interface,
                channel=self.channel,
                bitrate=self.bitrate,
                can_filters=self.can_filters
            )
            
            self._reader = AsyncBufferedReader()
            self._notifier = Notifier(
                self._bus, 
                [self._reader],
                loop=asyncio.get_running_loop()
            )
            self._is_configured = True
            
            logger.info(
                "CANBus configured",
                extra={
                    "interface": self.interface,
                    "channel": self.channel,
                    "bitrate": self.bitrate
                }
            )
        except CanError as e:
            await self._handle_can_error("Configuration failed", e)
            raise CANBusException(f"CAN bus configuration error: {str(e)}") from e

    async def stop(self) -> None:
        """Cleanly stop CAN bus interface and monitoring"""
        async with self._shutdown_lock:
            if not self._is_configured:
                return

            self._monitor_running = False
            if self._monitor_task:
                self._monitor_task.cancel()
                try:
                    await self._monitor_task
                except asyncio.CancelledError:
                    pass

            try:
                if self._notifier:
                    self._notifier.stop()
                if self._bus:
                    self._bus.shutdown()
                
                logger.info("CANBus stopped cleanly")
            except CanOperationError as e:
                await self._handle_can_error("Shutdown error", e)
            finally:
                self._is_configured = False
                self._bus = None
                self._reader = None
                self._notifier = None

    #region Message Handling
    @asynccontextmanager
    async def read_stream(
        self, 
        max_messages: int = 100,
        timeout: float = 1.0
    ) -> AsyncIterator[AsyncIterator[Dict[str, Any]]]:
        """Context manager for message streaming with protocol decoding"""
        if not self._is_configured:
            raise CANBusException("CANBus not configured")

        try:
            yield self._message_generator(max_messages, timeout)
        except CanError as e:
            await self._handle_can_error("Stream read error", e)
            raise CANBusException(f"Stream error: {str(e)}") from e

    async def _message_generator(
        self,
        max_messages: int,
        timeout: float
    ) -> AsyncIterator[Dict[str, Any]]:
        count = 0
        while count < max_messages:
            try:
                msg: Message = await asyncio.wait_for(
                    self._reader.get_message(),
                    timeout=timeout
                )
                
                if msg is None:  # Timeout or shutdown
                    break
                    
                CANBUS_MESSAGES_READ.labels(adapter_id=self.channel).inc()
                decoded = self.protocol.decode(msg.data)
                
                yield {
                    **decoded,
                    "arbitration_id": msg.arbitration_id,
                    "timestamp": msg.timestamp,
                    "is_error_frame": msg.is_error_frame,
                    "is_remote_frame": msg.is_remote_frame
                }
                count += 1
            except asyncio.TimeoutError:
                break  # Normal termination
            except CanError as e:
                await self._handle_can_error("Message read error", e)
                raise

    async def write_message(
        self, 
        arbitration_id: int, 
        data: Dict[str, Any],
        extended_id: bool = False
    ) -> None:
        """Write protocol-decoded message to CAN bus"""
        if not self._is_configured or not self._bus:
            raise CANBusException("CANBus not configured")
        
        try:
            encoded = self.protocol.encode(data)
            msg = Message(
                arbitration_id=arbitration_id,
                data=encoded,
                is_extended_id=extended_id
            )
            self._bus.send(msg)
            CANBUS_MESSAGES_WRITTEN.labels(adapter_id=self.channel).inc()
            logger.debug(f"Sent CAN message", extra={"message": msg})
        except CanError as e:
            CANBUS_WRITE_ERRORS.labels(adapter_id=self.channel).inc()
            await self._handle_can_error("Write error", e)
            raise CANBusException(f"Write failed: {str(e)}") from e
    #endregion

    #region Health Monitoring
    async def health_check(self) -> bool:
        """Check bus health by sending test message"""
        if not self._is_configured or not self._bus:
            logger.warning("Health check failed: CANBus not configured")
            CANBUS_HEALTH_CHECK_FAILS.labels(adapter_id=self.channel).inc()
            return False
        
        try:
            test_msg = Message(arbitration_id=0x7FF, is_remote_frame=True)
            self._bus.send(test_msg)
            CANBUS_HEALTH_CHECKS.labels(adapter_id=self.channel).inc()
            logger.debug("CANBus health check passed")
            return True
        except CanError as e:
            CANBUS_HEALTH_CHECK_FAILS.labels(adapter_id=self.channel).inc()
            await self._handle_can_error("Health check failed", e)
            return False

    async def start_monitoring(self, check_interval: float = 10.0):
        """Start background health monitoring"""
        if self._monitor_task:
            return
        
        self._monitor_running = True
        self._monitor_task = asyncio.create_task(
            self._monitor_loop(check_interval)
        )

    async def _monitor_loop(self, check_interval: float):
        while self._monitor_running:
            healthy = await self.health_check()
            if not healthy:
                logger.warning("CANBus unhealthy, attempting reconnection")
                try:
                    await self._reconnect()
                except CANBusException as e:
                    logger.error(f"Reconnection failed: {e}")
            await asyncio.sleep(check_interval)

    async def _reconnect(self, retries: int = 3, delay: float = 2.0) -> None:
        """Attempt to reconnect with retries"""
        for attempt in range(1, retries + 1):
            try:
                await self.stop()
                await self.configure()
                logger.info(f"CANBus reconnected on attempt {attempt}")
                return
            except CanError as e:
                logger.warning(f"Reconnect attempt {attempt} failed: {e}")
                await asyncio.sleep(delay)
        
        raise CANBusException("Failed to reconnect after multiple attempts")
    #endregion

    #region Protocol Management
    def set_protocol(self, protocol: Type[CANBusProtocol]):
        """Update the protocol implementation"""
        self.protocol = protocol()
        logger.info("Protocol updated", extra={"protocol": protocol.__name__})
    #endregion

    #region Common Utilities
    async def _handle_can_error(self, context: str, error: Exception) -> None:
        """Centralized error handling"""
        CANBUS_ERRORS.labels(adapter_id=self.channel).inc()
        logger.error(
            f"{context}: {str(error)}",
            exc_info=error,
            extra={
                "interface": self.interface,
                "channel": self.channel,
                "error_type": error.__class__.__name__
            }
        )
    #endregion
