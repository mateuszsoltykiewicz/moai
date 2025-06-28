class SecretNotFoundError(Exception):
    """Raised when a secret is not found"""
    pass

class SecretValidationError(Exception):
    """Raised when secret validation fails"""
    pass

class SecretPermissionError(Exception):
    """Raised when access to secret is unauthorized"""
    pass
