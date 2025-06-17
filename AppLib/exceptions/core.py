"""
Domain (core) exceptions for business rule violations.
"""

class DeviceError(Exception):
    """Base exception for device-related errors."""
    pass

class DeviceAlreadyActiveError(DeviceError):
    """Raised when attempting to activate an already active device."""
    pass

class DeviceAlreadyInactiveError(DeviceError):
    """Raised when attempting to deactivate an already inactive device."""
    pass

class InvalidDeviceStatusError(DeviceError):
    """Raised when a device has an invalid status."""
    pass

class UserError(Exception):
    """Base exception for user-related errors."""
    pass

class UserInactiveError(UserError):
    """Raised when an operation is attempted on an inactive user."""
    pass
