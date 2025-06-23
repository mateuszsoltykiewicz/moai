"""
Custom exceptions for SecretsManager.
"""

class SecretNotFoundError(Exception):
    """Raised when a secret is not found."""
    pass

class SecretValidationError(Exception):
    """Raised when secret validation fails."""
    pass
