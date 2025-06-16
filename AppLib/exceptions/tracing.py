from . import CoreException

class TracingNotAvailable(CoreException):
    """Raised if tracing is requested but OpenTelemetry is not installed."""
    pass