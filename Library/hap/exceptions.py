class HAPError(Exception):
    """Base HAP error"""

class HAPSetupError(HAPError):
    """Initialization failure"""

class HAPAccessoryError(HAPError):
    """Accessory-specific error"""

class HAPSecurityError(HAPError):
    """Security violation"""
