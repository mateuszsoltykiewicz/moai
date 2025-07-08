class RegistryError(Exception):
    """Base registry error"""
    pass

class ServiceNotFoundError(RegistryError):
    """Service not found error"""
    pass

class InstanceNotFoundError(RegistryError):
    """Instance not found error"""
    pass
