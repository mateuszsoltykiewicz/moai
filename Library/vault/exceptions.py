class VaultError(Exception):
    """Base Vault error"""

class VaultNotFoundError(VaultError):
    """Secret not found"""

class VaultConnectionError(VaultError):
    """Connection-related error"""

class VaultPermissionError(VaultError):
    """Permission denied"""

class VaultValidationError(VaultError):
    """Secret validation failed"""
