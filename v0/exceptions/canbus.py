from .base import AppLibException

class CANBusException(AppLibException):
    """General CAN bus error."""

class CANBusConnectionError(CANBusException):
    """Failed to connect to CAN bus."""

class CANBusTimeoutError(CANBusException):
    """CAN bus operation timed out."""

class CANBusProtocolError(CANBusException):
    """Protocol error in CAN message."""
