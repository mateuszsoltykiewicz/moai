from .base import AppLibException

class TracingException(AppLibException):
    """General tracing error."""

class SpanContextError(TracingException):
    """Error with span context propagation."""
