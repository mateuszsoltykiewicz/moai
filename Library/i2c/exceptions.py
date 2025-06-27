class I2CError(Exception):
    """Base I2C hardware error"""
    pass

class I2CDeviceNotFoundError(I2CError):
    """Device not found error"""
    pass

class I2CInvalidActionError(I2CError):
    """Invalid control action error"""
    pass

class I2CReadError(I2CError):
    """I2C read operation failed"""
    pass

class I2CWriteError(I2CError):
    """I2C write operation failed"""
    pass
