from Library.config import ConfigManager

class I2CConfig:
    @classmethod
    async def get_hardware_config(cls):
        return await ConfigManager.get("I2CAdapter/hardware")
    
    @classmethod
    async def get_security_config(cls):
        return await ConfigManager.get("I2CAdapter/security")
