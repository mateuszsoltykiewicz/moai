# adapters/update.py
import asyncio
from datetime import datetime
from typing import Optional
from pathlib import Path
import httpx
from pydantic import ValidationError
from core.config import AsyncConfigManager
from core.state import AppState
from models.config import AppConfig

class UpdateAdapter:
    def __init__(
        self, 
        config_manager: AsyncConfigManager,
        app_state: AppState,
        update_check_url: str = "https://api.your-update-server.com/v1/check"
    ):
        self.config_manager = config_manager
        self.app_state = app_state
        self.update_check_url = update_check_url
        self._http_client = httpx.AsyncClient()
        self._update_lock = asyncio.Lock()

    async def check_for_updates(self) -> dict:
        """Check for available updates from remote server"""
        current_config = await self.config_manager.get()
        
        try:
            response = await self._http_client.get(
                self.update_check_url,
                params={
                    "current_version": current_config.version,
                    "environment": current_config.environment
                }
            )
            response.raise_for_status()
            return response.json()
        except (httpx.HTTPError, ValidationError) as e:
            await self.app_state.update_state({
                "last_update_check": datetime.now(),
                "update_status": "check_failed",
                "update_error": str(e)
            }, persist=True)
            raise RuntimeError(f"Update check failed: {str(e)}")

    async def perform_update(self, version: Optional[str] = None) -> dict:
        """Perform atomic update operation with rollback support"""
        async with self._update_lock:
            try:
                # Get current state snapshot
                current_state = await self.app_state.get_state()
                
                # 1. Fetch new configuration
                new_config = await self._fetch_new_config(version)
                
                # 2. Validate configuration
                if not await self._validate_config(new_config):
                    raise ValueError("New configuration validation failed")
                
                # 3. Update application state
                await self.app_state.update_state({
                    "update_status": "in_progress",
                    "target_version": new_config.version,
                    "last_update_start": datetime.now()
                }, persist=True)
                
                # 4. Apply new configuration
                await self.config_manager.reload()
                
                # 5. Finalize state update
                await self.app_state.update_state({
                    "update_status": "completed",
                    "current_version": new_config.version,
                    "last_update_end": datetime.now(),
                    "update_error": None
                }, persist=True)
                
                return {"success": True, "new_version": new_config.version}
            
            except Exception as e:
                # Rollback to previous state
                await self.app_state.update_state({
                    "update_status": "failed",
                    "update_error": str(e),
                    **current_state.dict()
                }, persist=True)
                raise

    async def _fetch_new_config(self, version: Optional[str]) -> AppConfig:
        """Fetch new configuration from remote source"""
        current_config = await self.config_manager.get()
        params = {"environment": current_config.environment}
        if version:
            params["version"] = version
            
        try:
            response = await self._http_client.get(
                f"{self.update_check_url}/config",
                params=params
            )
            response.raise_for_status()
            return AppConfig.model_validate(response.json())
        except (httpx.HTTPError, ValidationError) as e:
            raise RuntimeError(f"Config fetch failed: {str(e)}")

    async def _validate_config(self, config: AppConfig) -> bool:
        """Perform extended config validation"""
        # Add custom validation logic here
        return True

    async def close(self):
        """Cleanup resources"""
        await self._http_client.aclose()
