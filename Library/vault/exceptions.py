"""
Custom exceptions for VaultManager.
"""

class VaultError(Exception):
    """Generic Vault error."""
    pass

class VaultNotFoundError(Exception):
    """Raised when a secret is not found."""
    pass
