from Library.config import ConfigManager

class DisasterDetectorConfig:
    @staticmethod
    async def get_config():
        return await ConfigManager.get("DisasterDetector")
