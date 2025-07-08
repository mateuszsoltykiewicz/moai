class VaultError(Exception):
    """Base Vault error"""
    pass

class VaultNotFoundError(VaultError):
    """Secret not found"""
    pass

class VaultConnectionError(VaultError):
    """Connection-related error"""
    pass

class VaultPermissionError(VaultError):
    """Permission denied"""
    pass

class VaultValidationError(VaultError):
    """Secret validation failed"""
    pass
