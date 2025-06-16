from .base import AppLibException

class I2CException(AppLibException):
    """General I2C error."""

class I2CConnectionError(I2CException):
    """Failed to connect to I2C device."""

class I2CCommandError(I2CException):
    """Invalid or failed I2C command."""
