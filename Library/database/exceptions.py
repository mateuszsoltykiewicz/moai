"""
Custom exceptions for DatabaseManager.
"""

class DatabaseError(Exception):
    """Generic error for DatabaseManager operations."""
    pass

class RecordNotFoundError(Exception):
    """Raised when a database record is not found."""
    pass
