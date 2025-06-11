"""
core/exceptions.py

Centralized exception hierarchy for all subservices and core modules.

- All subservice and core exceptions should inherit from CoreException.
- Use specific exception classes for common error categories.
- Subservices can extend these base classes for their own needs.
"""

class CoreException(Exception):
    """
    Base exception for all application errors.
    Use this as the root for all custom exceptions.
    """
    def __init__(self, message: str, *, code: int = None, details: dict = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}

    def __str__(self):
        base = f"{self.__class__.__name__}: {self.message}"
        if self.code is not None:
            base += f" (code={self.code})"
        if self.details:
            base += f" details={self.details}"
        return base

class ConfigException(CoreException):
    """Raised for configuration errors."""
    pass

class StateException(CoreException):
    """Raised for state management errors."""
    pass

class ValidationException(CoreException):
    """Raised for schema or input validation errors."""
    pass

class MTLSException(CoreException):
    """Raised for mTLS/certificate errors."""
    pass

class AlarmException(CoreException):
    """Raised for alarm/alerting errors."""
    pass

class MetricsException(CoreException):
    """Raised for metrics/monitoring errors."""
    pass

class EventException(CoreException):
    """Raised for event bus or pub/sub errors."""
    pass

# Add more as needed for your core domains.
