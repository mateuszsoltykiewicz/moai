from .base import AppLibException

class VaultException(AppLibException):
    """General Vault error."""

class SecretNotFoundException(VaultException):
    """Requested secret was not found."""

class VaultAuthenticationError(VaultException):
    """Vault authentication failed."""
