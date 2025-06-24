# adapters/vault.py

import os
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager
import hvac
from hvac import AsyncClient
from pydantic import ValidationError

from core.config import AsyncConfigManager
from core.exceptions import VaultException, SecretNotFoundException
from metrics.secrets import (
    VAULT_SECRET_READS,
    VAULT_SECRET_WRITES,
    VAULT_SECRET_DELETES,
    VAULT_ERRORS,
    VAULT_LATENCY
)
from core.logging import get_logger

logger = get_logger(__name__)

class AsyncVaultAdapter:
    def __init__(self, config_manager: AsyncConfigManager):
        self.config_manager = config_manager
        self.client: Optional[AsyncClient] = None
        self._lock = asyncio.Lock()
        self._cache = {}
        self._last_auth = datetime.min
        self._token_ttl = 0

    @asynccontextmanager
    async def context(self):
        """Async context manager for automatic auth and cleanup."""
        try:
            await self.authenticate()
            yield self
        finally:
            await self.close()

    async def authenticate(self) -> None:
        """Authenticate using configured method."""
        config = await self.config_manager.get()
        async with self._lock:
            if self.client and await self._is_token_valid():
                return
            self.client = AsyncClient(url=config.vault.address)
            self.client.token = config.vault.token
            await self._validate_token()
            logger.info("Vault authentication successful")

    async def _is_token_valid(self) -> bool:
        # For simplicity, re-authenticate every 80% of the token TTL
        return (datetime.utcnow() - self._last_auth) < timedelta(seconds=self._token_ttl * 0.8)

    async def _validate_token(self) -> None:
        try:
            if not await self.client.is_authenticated():
                raise VaultException("Token validation failed")
        except Exception as e:
            raise VaultException("Token validation error") from e

    async def get_dynamic_db_credentials(self, role_name: str, mount_point: str = "database") -> Dict[str, Any]:
        """
        Fetch dynamic database credentials for a given role.
        These are short-lived and should be refreshed on lease expiry or DB auth failure.
        """
        try:
            creds = await self.client.secrets.database.generate_credentials(
                name=role_name,
                mount_point=mount_point
            )
            lease_id = creds["lease_id"]
            lease_duration = creds["lease_duration"]
            username = creds["data"]["username"]
            password = creds["data"]["password"]
            VAULT_SECRET_READS.labels(cached=False).inc()
            return {
                "username": username,
                "password": password,
                "lease_id": lease_id,
                "lease_duration": lease_duration,
                "expire_at": datetime.utcnow() + timedelta(seconds=lease_duration)
            }
        except Exception as e:
            VAULT_ERRORS.labels(error_type="db_dynamic_read").inc()
            logger.error(f"Failed to fetch dynamic DB credentials: {e}")
            raise VaultException(f"Failed to fetch dynamic DB credentials: {str(e)}")

    async def renew_db_lease(self, lease_id: str) -> Dict[str, Any]:
        """
        Renew a dynamic DB credential lease.
        """
        try:
            result = await self.client.sys.renew_lease(lease_id=lease_id)
            return result
        except Exception as e:
            VAULT_ERRORS.labels(error_type="db_lease_renew").inc()
            logger.error(f"Failed to renew DB lease: {e}")
            raise VaultException(f"Failed to renew DB lease: {str(e)}")

    async def revoke_db_lease(self, lease_id: str) -> None:
        """
        Revoke a dynamic DB credential lease.
        """
        try:
            await self.client.sys.revoke_lease(lease_id=lease_id)
        except Exception as e:
            VAULT_ERRORS.labels(error_type="db_lease_revoke").inc()
            logger.error(f"Failed to revoke DB lease: {e}")
            raise VaultException(f"Failed to revoke DB lease: {str(e)}")

    async def get_static_db_credentials(self, role_name: str, mount_point: str = "database") -> Dict[str, Any]:
        """
        Fetch static database credentials for a given role.
        These are rotated by Vault on a schedule or via manual trigger.
        """
        try:
            creds = await self.client.secrets.database.read_static_credentials(
                name=role_name,
                mount_point=mount_point
            )
            username = creds["data"]["username"]
            password = creds["data"]["password"]
            VAULT_SECRET_READS.labels(cached=False).inc()
            return {
                "username": username,
                "password": password
            }
        except Exception as e:
            VAULT_ERRORS.labels(error_type="db_static_read").inc()
            logger.error(f"Failed to fetch static DB credentials: {e}")
            raise VaultException(f"Failed to fetch static DB credentials: {str(e)}")

    async def rotate_static_db_credentials(self, role_name: str, mount_point: str = "database") -> Dict[str, Any]:
        """
        Manually rotate static role credentials and fetch the new password.
        """
        try:
            await self.client.secrets.database.rotate_static_role_credentials(
                name=role_name,
                mount_point=mount_point
            )
            # Fetch the new credentials after rotation
            new_creds = await self.get_static_db_credentials(role_name, mount_point)
            return new_creds
        except Exception as e:
            VAULT_ERRORS.labels(error_type="db_static_rotate").inc()
            logger.error(f"Failed to rotate static DB credentials: {e}")
            raise VaultException(f"Failed to rotate static DB credentials: {str(e)}")

    async def rotate_root_db_credentials(self, db_config_name: str, mount_point: str = "database") -> None:
        """
        Rotate the root credentials for a database connection.
        """
        try:
            await self.client.secrets.database.rotate_root_credentials(
                name=db_config_name,
                mount_point=mount_point
            )
            logger.info(f"Root credentials rotated for DB config: {db_config_name}")
        except Exception as e:
            VAULT_ERRORS.labels(error_type="db_root_rotate").inc()
            logger.error(f"Failed to rotate root DB credentials: {e}")
            raise VaultException(f"Failed to rotate root DB credentials: {str(e)}")

    async def close(self) -> None:
        """Cleanup resources."""
        if self.client:
            try:
                await self.client.close()
            except Exception:
                pass
        self.client = None
