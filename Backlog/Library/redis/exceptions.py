class RedisConnectionError(Exception):
    """Raised when Redis connection fails"""
    pass

class RedisOperationError(Exception):
    """Raised when Redis operation fails"""
    pass
