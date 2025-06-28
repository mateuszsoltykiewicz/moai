class HealthManagerError(Exception):
    """Base exception for HealthManager"""
    pass

class HealthCheckTimeoutError(HealthManagerError):
    """Exception for health check timeout"""
    pass

class HealthCheckFailedError(HealthManagerError):
    """Exception for health check failure"""
    pass
