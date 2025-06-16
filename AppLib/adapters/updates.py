# adapters/update.py
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Optional, AsyncIterator, Dict, Any

import httpx
from pydantic import ValidationError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from core.config import AsyncConfigManager
from core.exceptions import UpdateException
from core.logging import get_logger
from core.state import AppState
from metrics.updates import (
    UPDATES_STARTED,
    UPDATES_COMPLETED,
    UPDATES_FAILED,
    UPDATE_DURATION,
    UPDATE_RETRIES
)
from models.config import AppConfig

logger = get_logger(__name__)

class UpdateAdapter:
    def __init__(
        self, 
        config_manager: AsyncConfigManager,
        app_state: AppState,
        update_check_url: str = "https://api.your-update-server.com/v1/check",
        timeout: float = 10.0,
        max_retries: int = 3
    ):
        self.config_manager = config_manager
        self.app_state = app_state
        self.update_check_url = update_check_url
        self.timeout = timeout
        self.max_retries = max_retries
        self._http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout),
            limits=httpx.Limits(max_connections=5)
        )
        self._update_lock = asyncio.Lock()
        self._active_update = False

    @asynccontextmanager
    async def update_context(self) -> AsyncIterator[Dict[str, Any]]:
        """Async context manager for atomic updates"""
        async with self._update_lock:
            if self._active_update:
                raise UpdateException("Update already in progress")
            
            self._active_update = True
            start_time = datetime.utcnow()
            UPDATES_STARTED.inc()
            
            try:
                state_before = await self.app_state.get_state()
                yield {"start_time": start_time}
                
                duration = (datetime.utcnow() - start_time).total_seconds()
                UPDATE_DURATION.observe(duration)
                UPDATES_COMPLETED.inc()
            except Exception as e:
                duration = (datetime.utcnow() - start_time).total_seconds()
                UPDATE_DURATION.observe(duration)
                UPDATES_FAILED.inc()
                await self._rollback_update(state_before)
                raise
            finally:
                self._active_update = False

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(httpx.NetworkError),
        before_sleep=lambda _: UPDATE_RETRIES.inc()
    )
    async def check_for_updates(self) -> Dict[str, Any]:
        """Check for available updates with exponential backoff"""
        current_config = await self.config_manager.get()
        
        try:
            response = await self._http_client.get(
                self.update_check_url,
                params={
                    "current_version": current_config.version,
                    "environment": current_config.environment,
                    "component": "main"
                },
                headers={"Authorization": f"Bearer {current_config.update_token}"}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            await self._log_update_error("HTTP error during update check", e)
            raise UpdateException(f"Update server error: {e.response.text}") from e
        except ValidationError as e:
            await self._log_update_error("Invalid update response format", e)
            raise UpdateException("Invalid update server response") from e

    async def perform_update(self, version: Optional[str] = None) -> Dict[str, Any]:
        """Perform atomic update with automatic rollback on failure"""
        async with self.update_context() as context:
            current_config = await self.config_manager.get()
            new_config = await self._fetch_validated_config(version)
            
            # Create restore point
            restore_point = await self._create_restore_point()
            
            try:
                # Stage 1: Prepare update
                await self._update_app_state("preparing", new_config.version)
                
                # Stage 2: Validate dependencies
                await self._validate_dependencies(new_config)
                
                # Stage 3: Apply configuration
                await self.config_manager.apply(new_config)
                
                # Stage 4: Finalize
                await self._update_app_state("completed", new_config.version)
                
                return {
                    "success": True,
                    "old_version": current_config.version,
                    "new_version": new_config.version
                }
            except Exception as e:
                await self._restore(restore_point)
                raise

    async def _fetch_validated_config(self, version: str) -> AppConfig:
        """Fetch and validate new configuration"""
        try:
            config_data = await self._fetch_config_data(version)
            config = AppConfig.model_validate(config_data)
            
            # Custom validation
            if not config.compatible_with_current:
                raise UpdateException("New config is incompatible with current state")
                
            return config
        except ValidationError as e:
            await self._log_update_error("Config validation failed", e)
            raise UpdateException("Invalid configuration format") from e

    async def _fetch_config_data(self, version: str) -> Dict[str, Any]:
        """Protected method to fetch raw config data"""
        current_config = await self.config_manager.get()
        params = {"environment": current_config.environment}
        if version:
            params["version"] = version
            
        try:
            response = await self._http_client.get(
                f"{self.update_check_url}/config",
                params=params,
                headers={"Authorization": f"Bearer {current_config.update_token}"}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            await self._log_update_error("Config fetch failed", e)
            raise UpdateException(f"Config download failed: {e.response.text}") from e

    async def _update_app_state(self, status: str, version: str) -> None:
        """Update application state with version and status"""
        await self.app_state.update_state({
            "update_status": status,
            "target_version": version,
            "last_update_phase": datetime.utcnow()
        }, persist=True)

    async def _create_restore_point(self) -> Dict[str, Any]:
        """Create system restore point"""
        return {
            "config": await self.config_manager.get(),
            "state": await self.app_state.get_state()
        }

    async def _restore(self, restore_point: Dict[str, Any]) -> None:
        """Restore system from backup"""
        try:
            await self.config_manager.apply(restore_point["config"])
            await self.app_state.update_state(restore_point["state"], persist=True)
            logger.warning("System restored from backup")
        except Exception as e:
            logger.critical("Failed to restore system from backup!", exc_info=e)
            raise UpdateException("Critical failure during rollback") from e

    async def _validate_dependencies(self, config: AppConfig) -> None:
        """Validate system dependencies for new config"""
        # Implement checks for database schemas, service versions, etc.
        if config.requires_migration and not await self._check_migration_capability():
            raise UpdateException("Database migration required but not supported")

    async def _log_update_error(self, context: str, error: Exception) -> None:
        """Centralized error logging"""
        logger.error(
            f"{context}: {str(error)}",
            exc_info=error,
            extra={
                "update_phase": "check",
                "environment": (await self.config_manager.get()).environment
            }
        )

    async def close(self) -> None:
        """Cleanup resources"""
        await self._http_client.aclose()
