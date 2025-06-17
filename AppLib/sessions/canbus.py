# sessions/canbus.py

import can
import logging
from typing import Optional

class CANBusSessionManager:
    def __init__(self, channel: str, bustype: str = "socketcan", can_filters: Optional[list] = None, **kwargs):
        self.channel = channel
        self.bustype = bustype
        self.can_filters = can_filters
        self.kwargs = kwargs
        self.bus: Optional[can.Bus] = None
        self.logger = logging.getLogger("CANBusSessionManager")

    def __enter__(self) -> can.Bus:
        try:
            self.bus = can.Bus(channel=self.channel, bustype=self.bustype, can_filters=self.can_filters, **self.kwargs)
            self.logger.info(f"CAN bus {self.channel} opened.")
            return self.bus
        except Exception as exc:
            self.logger.error(f"Failed to open CAN bus {self.channel}: {exc}")
            raise

    def __exit__(self, exc_type, exc, tb):
        if self.bus:
            try:
                self.bus.shutdown()
                self.logger.info(f"CAN bus {self.channel} closed.")
            except Exception as exc:
                self.logger.warning(f"Error closing CAN bus {self.channel}: {exc}")
