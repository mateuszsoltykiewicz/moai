import asyncio
from typing import Dict, Any
from Library.vault import VaultManager
from Library.state import StateManager
from Library.registry import RegistryClient
from Library.logging import get_logger
from Library.config import ConfigManager

logger = get_logger(__name__)

class ConfigServerManager:
    _cache: Dict[str, Dict[str, Any]] = {}
    _lock = asyncio.Lock()

    @classmethod
    async def setup(cls):
        """Initialize configuration server resources"""
        # Register with service registry
        await RegistryClient.register_service(
            name="configuration-server",
            url="http://configuration-server:8000"
        )
        # Initialize Vault connection
        await VaultManager.setup()
        logger.info("ConfigurationServer resources initialized")

    @classmethod
    async def shutdown(cls):
        """Cleanup configuration server resources"""
        await VaultManager.shutdown()
        logger.info("ConfigurationServer resources released")

    @classmethod
    async def get_config(cls, service: str, version: str = "latest") -> Dict[str, Any]:
        """Get configuration with caching"""
        cache_key = f"{service}:{version}"
        
        async with cls._lock:
            if cache_key in cls._cache:
                return cls._cache[cache_key]
            
            # Load from Vault
            config = await VaultManager.read_secret(f"config/{service}/{version}")
            if not config:
                config = await ConfigManager.get(service, version)
            
            cls._cache[cache_key] = config
            return config

    @classmethod
    async def reload_config(cls, service: str):
        """Reload configuration for a service"""
        async with cls._lock:
            # Clear cache for service
            keys_to_clear = [k for k in cls._cache if k.startswith(f"{service}:")]
            for key in keys_to_clear:
                del cls._cache[key]
            logger.info(f"Config reloaded for {service}")
