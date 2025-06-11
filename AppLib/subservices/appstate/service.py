"""
AppStateSubService integrates state management with other services
"""

from AppLib.core.state import AppState
from AppLib.subservices.base import SubServiceBase
from AppLib.subservices.secrets.manager import SecretsManager

class AppStateSubService(SubServiceBase):
    def __init__(self, secrets_manager: SecretsManager):
        self._state = AppState()
        self._secrets = secrets_manager

    async def start(self):
        """Initialize state with secrets integration"""
        config = await self._secrets.get_config()
        await self._state.initialize(config)
        
        if config.persistence.auto_backup:
            await self._state.start_auto_backup(config.persistence.backup_interval)

    async def stop(self):
        """Clean shutdown with state persistence"""
        await self._state.stop_auto_backup()
        await self._state._persist_state()

    async def get_state(self):
        """Expose state to other services"""
        return await self._state.get_state()

    async def update_connection_state(self, service: str, status: dict):
        """Example state update method"""
        await self._state.update_state({
            "connections": {service: status}
        }, persist=True)
