class I2CAdapterError(Exception):
    """Base I2C Adapter error"""
    pass

class InvalidCommandError(I2CAdapterError):
    """Invalid command requested"""
    pass

class CriticalHardwareError(I2CAdapterError):
    """Critical hardware failure"""
    pass
