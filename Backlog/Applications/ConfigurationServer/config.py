from Library.config import ConfigManager

class ConfigServerConfig:
    @staticmethod
    async def get_server_config():
        """Get ConfigurationServer's own configuration"""
        return await ConfigManager.get("ConfigurationServer")
