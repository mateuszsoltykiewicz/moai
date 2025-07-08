class HAPError(Exception):
    """Base HAP error"""
    pass

class HAPSetupError(HAPError):
    """Initialization failure"""
    pass

class HAPAccessoryError(HAPError):
    """Accessory-specific error"""
    pass

class HAPSecurityError(HAPError):
    """Security violation"""
    pass
