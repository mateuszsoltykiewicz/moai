class ConfigServerError(Exception):
    """Base ConfigurationServer error"""
    pass

class ConfigNotFoundError(ConfigServerError):
    """Configuration not found error"""
    pass

class ConfigReloadError(ConfigServerError):
    """Configuration reload error"""
    pass
