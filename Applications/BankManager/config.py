from Library.config import ConfigManager

class BankManagerConfig:
    @staticmethod
    async def get_config():
        return await ConfigManager.get("BankManager")
