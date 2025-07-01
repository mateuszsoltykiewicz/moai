from Library.config import ConfigManager

class StateServerConfig:
    @staticmethod
    async def get_server_config():
        return await ConfigManager.get("StateServer")
