"""
Session/resource management exceptions.
"""

class SessionError(Exception):
    """Base exception for session/connection errors."""
    pass

class ConnectionFailed(SessionError):
    """Raised when a connection to a resource fails."""
    pass

class ResourceTimeout(SessionError):
    """Raised when a session/resource times out."""
    pass
