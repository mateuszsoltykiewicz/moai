"""
Custom exceptions for AdapterManager.
"""

class AdapterNotFoundError(Exception):
    """Raised when an adapter type is not found."""
    pass

class AdapterCreationError(Exception):
    """Raised when adapter instance creation fails."""
    pass
