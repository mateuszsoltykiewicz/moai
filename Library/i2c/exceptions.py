"""
Custom exceptions for I2CManager.
"""

class I2CError(Exception):
    """Generic error for I2CManager operations."""
    pass

class I2CDeviceNotFoundError(Exception):
    """Raised when an I2C device or relay is not found."""
    pass
