class RegistryError(Exception):
    pass

class ServiceNotFoundError(RegistryError):
    pass

class InstanceNotFoundError(RegistryError):
    pass
