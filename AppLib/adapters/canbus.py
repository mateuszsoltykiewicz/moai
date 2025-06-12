import asyncio
from fastapi import status
import can
from typing import Optional, List, Dict, Any
from core.exceptions import CANBusException, APIException

class CANBusAdapter:
    def __init__(self, channel: str, bitrate: int):
        self.channel = channel
        self.bitrate = bitrate
        self.bus: Optional[can.Bus] = None
        self.reader: Optional[can.AsyncBufferedReader] = None
        self.notifier: Optional[can.Notifier] = None
        self._streaming = False

    async def configure(self, filters: Optional[List[Dict[str, Any]]] = None):
        try:
            # Initialize CAN bus interface (python-can)
            self.bus = can.Bus(
                interface="socketcan",  # or "virtual", "pcan", etc.
                channel=self.channel,
                bitrate=self.bitrate
            )
            if filters:
                self.bus.set_filters(filters)
            self.reader = can.AsyncBufferedReader()
            self.notifier = can.Notifier(self.bus, [self.reader], loop=asyncio.get_running_loop())
            self._streaming = True
        except CANBusException as e:
            raise APIException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=str(e)
            )

    async def stop(self):
        self._streaming = False
        if self.notifier:
            self.notifier.stop()
        if self.bus:
            self.bus.shutdown()

    async def read_stream(self, max_messages: int = 100):
        """Yield CAN messages as they arrive."""
        count = 0
        while self._streaming and count < max_messages:
            msg = await self.reader.get_message()
            yield {
                "arbitration_id": msg.arbitration_id,
                "data": list(msg.data),
                "timestamp": msg.timestamp
            }
            count += 1
