from Library.config import ConfigManager

class ServiceDiscoveryConfig:
    @staticmethod
    async def get_config():
        return await ConfigManager.get("ServiceDiscovery")
