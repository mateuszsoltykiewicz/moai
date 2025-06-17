from . import CoreException

class MetricsException(CoreException):
    """Raised for metrics/monitoring errors."""
    pass

class MetricsError(Exception):
    """Base exception for metrics/observability errors."""
    pass

class MetricRegistrationError(MetricsError):
    """Raised when metric registration fails."""
    pass
