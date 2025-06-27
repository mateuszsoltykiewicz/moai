class SecretNotFoundError(Exception):
    pass

class SecretValidationError(Exception):
    pass

class SecretPermissionError(Exception):
    """Raised when access to secret is unauthorized"""
    pass

class SecretConcurrencyError(Exception):
    """Raised when secret version conflict occurs"""
    pass
