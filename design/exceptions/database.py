from .base import AppLibException

class DatabaseException(AppLibException):
    """General database error."""

class DatabaseConnectionError(DatabaseException):
    """Failed to connect to database."""

class DatabaseQueryError(DatabaseException):
    """Database query failed."""
