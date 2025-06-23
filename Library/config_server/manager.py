# config_server/manager.py
import os
import asyncio
from typing import Dict, Any
from .schemas import ConfigResponse
from .backends.git import GitConfigBackend
from .backends.vault import VaultSecretBackend
from .notifier import ConfigChangeNotifier

class ConfigServer:
    def __init__(self, repo_url: str, vault_addr: str):
        self.git_backend = GitConfigBackend(repo_url)
        self.vault_backend = VaultSecretBackend(vault_addr)
        self.notifier = ConfigChangeNotifier()
        self.cache: Dict[str, Dict[str, Any]] = {}
        
    async def start(self):
        """Initialize connections"""
        await self.git_backend.connect()
        await self.vault_backend.connect()
        asyncio.create_task(self._watch_changes())
    
    async def get_config(self, service: str, env: str) -> ConfigResponse:
        """Get configuration for a service"""
        if service not in self.cache:
            config = await self.git_backend.get_config(service, env)
            secrets = await self._resolve_secrets(config.get("secrets", []))
            self.cache[service] = {**config, **secrets}
        return ConfigResponse(config=self.cache[service], version=self.git_backend.current_commit)
    
    async def _resolve_secrets(self, secret_paths: list) -> Dict[str, str]:
        """Resolve secrets from Vault"""
        secrets = {}
        for path in secret_paths:
            secrets[path.split("/")[-1]] = await self.vault_backend.get_secret(path)
        return secrets
    
    async def _watch_changes(self):
        """Monitor config repository for changes"""
        async for commit_id in self.git_backend.watch_changes():
            changed_services = self.git_backend.get_changed_services(commit_id)
            for service in changed_services:
                if service in self.cache:
                    del self.cache[service]
                await self.notifier.notify(service)
