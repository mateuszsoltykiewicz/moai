"""
General-purpose utility exceptions.
"""

class ConfigValidationError(Exception):
    """Raised when configuration validation fails."""
    pass

class SecretRedactionError(Exception):
    """Raised when redaction of sensitive data fails."""
    pass
