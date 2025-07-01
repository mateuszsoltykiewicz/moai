import asyncio
from typing import List
from .schemas import Accessory
from Library.logging import get_logger
from Library.state import StateClient
from Library.config import ConfigManager
from Library.alarms import AlarmClient
from Library.registry import RegistryClient
from .ws import broadcast_update

logger = get_logger(__name__)

class HomeKitBridgeManager:
    _lock = asyncio.Lock()
    _state_client = StateClient(service_name="HomeKitBridge")
    _config_manager = ConfigManager()
    _alarm_client = AlarmClient()
    _registry_client = RegistryClient()
    _accessories: List[Accessory] = []

    @classmethod
    async def update_accessory_state(cls, accessory: Accessory):
        # Called whenever accessory state changes
        await broadcast_update(accessory.dict())

    @classmethod
    async def setup(cls):
        await cls._state_client.setup()
        await cls._refresh_from_registry()
        logger.info("HomeKitBridgeManager setup complete")

    @classmethod
    async def shutdown(cls):
        await cls._state_client.shutdown()
        logger.info("HomeKitBridgeManager shutdown complete")

    @classmethod
    async def list_accessories(cls) -> List[Accessory]:
        async with cls._lock:
            return cls._accessories

    @classmethod
    async def refresh_accessories(cls):
        async with cls._lock:
            await cls._refresh_from_registry()
            logger.info("Accessories refreshed from StateRegistry")

    @classmethod
    async def _refresh_from_registry(cls):
        """Fetch accessories and schemas from StateRegistry/ConfigServer."""
        try:
            registry_accessories = await cls._registry_client.get_accessories()
            config = await cls._config_manager.get("HomeKitBridge")
            cls._accessories = [
                Accessory(
                    id=acc.get("id"),
                    name=acc.get("name"),
                    type=acc.get("type"),
                    status=acc.get("status", "unknown")
                ) for acc in registry_accessories
            ]
            # Raise alarm if any required backend is unreachable
            for acc in cls._accessories:
                if acc.status != "online":
                    await cls._alarm_client.raise_alarm(
                        alarm_id=f"ACCESSORY_{acc.id}_UNREACHABLE",
                        message=f"Accessory {acc.name} is unreachable",
                        severity="WARNING"
                    )
        except Exception as e:
            logger.error(f"Failed to refresh accessories: {e}")
            await cls._alarm_client.raise_alarm(
                alarm_id="HOMEKIT_REFRESH_FAILED",
                message="Failed to refresh HomeKit accessories",
                severity="FATAL"
            )
