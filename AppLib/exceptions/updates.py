from .base import AppLibException

class UpdateException(AppLibException):
    """General update error."""

class UpdateCheckError(UpdateException):
    """Update check failed."""

class UpdateApplyError(UpdateException):
    """Failed to apply update."""
