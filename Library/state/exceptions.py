"""
Custom exceptions for StateManager.
"""

class StateValidationError(Exception):
    """Raised when state validation fails."""
    pass

class StateNotFoundError(Exception):
    """Raised when state key is not found."""
    pass
