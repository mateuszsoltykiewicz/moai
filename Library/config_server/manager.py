import asyncio
import os
from typing import Dict, Any
from .backends.git import GitConfigBackend
from .backends.vault import VaultSecretBackend
from .notifier import ConfigChangeNotifier
from .schemas import ConfigResponse
from .metrics import record_config_operation
from .utils import log_info, log_error
from Library.metrics.manager import MetricsManager

class ConfigServer:
    def __init__(self, repo_url: str, vault_addr: str, metrics_manager: MetricsManager):
        self.git_backend = GitConfigBackend(repo_url)
        self.vault_backend = VaultSecretBackend(vault_addr)
        self.notifier = ConfigChangeNotifier()
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.metrics = metrics_manager
        self._lock = asyncio.Lock()
        
    async def start(self):
        """Secure initialization with error handling"""
        try:
            await self.git_backend.connect()
            await self.vault_backend.connect()
            asyncio.create_task(self._watch_changes())
            log_info("ConfigServer started")
        except Exception as e:
            log_error(f"ConfigServer startup failed: {e}")
            raise

    async def get_config(self, service: str, env: str) -> ConfigResponse:
        """Cached config retrieval with metrics"""
        cache_key = f"{service}:{env}"
        async with self._lock:
            if cache_key not in self.cache:
                config = await self.git_backend.get_config(service, env)
                secrets = await self._resolve_secrets(config.get("secrets", []))
                self.cache[cache_key] = {**config, **secrets}
                record_config_operation("config_fetch")
            return ConfigResponse(
                config=self.cache[cache_key],
                version=self.git_backend.current_commit
            )
    
    async def _resolve_secrets(self, secret_paths: list) -> Dict[str, str]:
        """Batched secret resolution with error handling"""
        secrets = {}
        for path in secret_paths:
            try:
                secret_name = path.split("/")[-1]
                secrets[secret_name] = await self.vault_backend.get_secret(path)
            except Exception as e:
                log_error(f"Secret resolution failed for {path}: {e}")
        return secrets
    
    async def _watch_changes(self):
        """Efficient change detection with backoff"""
        while True:
            try:
                async for commit_id in self.git_backend.watch_changes():
                    changed_services = self.git_backend.get_changed_services(commit_id)
                    for service in changed_services:
                        # Invalidate cache for changed services
                        for key in list(self.cache.keys()):
                            if key.startswith(f"{service}:"):
                                del self.cache[key]
                        await self.notifier.notify(service)
                        record_config_operation("config_update")
            except Exception as e:
                log_error(f"Config watch error: {e}. Retrying in 10s")
                await asyncio.sleep(10)
