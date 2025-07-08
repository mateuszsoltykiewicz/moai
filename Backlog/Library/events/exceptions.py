class EventValidationError(Exception):
    """Raised when an event payload fails schema validation."""
    pass

class EventBusError(Exception):
    """Generic error for event bus operations."""
    pass
