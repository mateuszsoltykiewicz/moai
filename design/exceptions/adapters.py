from . import CoreException

class AdapterException(CoreException):
    """Generic hardware adapter exception (for future use)."""
    pass

class AdapterError(Exception):
    """Base exception for adapter-related errors."""
    pass

class ExternalServiceUnavailable(AdapterError):
    """Raised when an external service is unavailable."""
    pass

class ProtocolError(AdapterError):
    """Raised for protocol-specific errors (e.g., Kafka, HTTP, I2C)."""
    pass
