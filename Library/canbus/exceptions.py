"""
Custom exceptions for CanbusManager.
"""

class CanbusError(Exception):
    """Generic error for CanbusManager operations."""
    pass

class CanbusSensorNotFoundError(Exception):
    """Raised when a CANBus sensor is not found."""
    pass
