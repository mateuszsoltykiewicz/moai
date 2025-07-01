from Library.config import ConfigManager

class AlarmsServerConfig:
    @staticmethod
    async def get_config():
        return await ConfigManager.get("AlarmsServer")
