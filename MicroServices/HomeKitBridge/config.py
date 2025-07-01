from Library.config import ConfigManager

class HomeKitBridgeConfig:
    @staticmethod
    async def get_config():
        return await ConfigManager.get("HomeKitBridge")
