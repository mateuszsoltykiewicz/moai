from Library.config import ConfigManager

class ExceptionsServerConfig:
    @staticmethod
    async def get_config():
        return await ConfigManager.get("ExceptionsServer")
