class AlertManagerError(Exception):
    """Base AlertManager exception"""

class AlertManagerConnectionError(AlertManagerError):
    """Connection-related error"""

class AlertManagerAPIError(AlertManagerError):
    """API returned error status"""
    
class AlertManagerConfigError(AlertManagerError):
    """Invalid configuration"""
