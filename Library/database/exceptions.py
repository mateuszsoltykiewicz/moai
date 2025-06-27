"""
Custom exceptions for DatabaseManager.
"""

class DatabaseError(Exception):
    """Base database error"""
    pass

class RecordNotFoundError(DatabaseError):
    """Record not found error"""
    pass

class TableNotConfiguredError(DatabaseError):
    """Table not configured error"""
    pass
