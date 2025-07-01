from Library.config import ConfigManager

class HeatingJobConfig:
    @staticmethod
    async def get_config():
        return await ConfigManager.get("HeatingJob")
