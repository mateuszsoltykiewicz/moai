from Library.config import ConfigManager

class CANBusAdapterConfig:
    @staticmethod
    async def get_config():
        return await ConfigManager.get("CANBusAdapter")
