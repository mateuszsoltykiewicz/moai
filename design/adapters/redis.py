import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator, Optional
import aioredis
from tenacity import retry, stop_after_attempt, wait_exponential

from core.config import AsyncConfigManager
from core.logging import get_logger
from metrics.redis import (
    REDIS_CONNECTIONS,
    REDIS_COMMANDS,
    REDIS_ERRORS,
    REDIS_CACHE_HITS,
    REDIS_CACHE_MISSES
)

logger = get_logger(__name__)

class RedisAdapter:
    def __init__(self, config_manager: AsyncConfigManager):
        self.config_manager = config_manager
        self.pool: Optional[aioredis.Redis] = None

    @asynccontextmanager
    async def connection(self) -> AsyncIterator[aioredis.Redis]:
        """Async context manager for Redis connections"""
        config = await self.config_manager.get()
        try:
            self.pool = await aioredis.from_url(
                config.redis.url,
                password=config.redis.password,
                max_connections=config.redis.pool_size
            )
            REDIS_CONNECTIONS.inc()
            yield self.pool
        except Exception as e:
            REDIS_ERRORS.inc()
            logger.error(f"Redis error: {str(e)}")
            raise
        finally:
            if self.pool:
                await self.pool.close()
                REDIS_CONNECTIONS.dec()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def get(self, key: str) -> Optional[str]:
        """Get value from Redis with cache metrics"""
        async with self.connection() as redis:
            value = await redis.get(key)
            REDIS_COMMANDS.inc()
            if value:
                REDIS_CACHE_HITS.inc()
                return value.decode()
            REDIS_CACHE_MISSES.inc()
            return None

    async def set(self, key: str, value: str, ttl: int = 3600) -> None:
        """Set value in Redis with TTL"""
        async with self.connection() as redis:
            await redis.set(key, value, ex=ttl)
            REDIS_COMMANDS.inc()
