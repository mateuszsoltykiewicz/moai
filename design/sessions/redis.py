"""
Async Redis Session Manager

- Manages async Redis connections and pooling.
- Provides context manager interface for safe resource handling.
- Integrates with aioredis for high-performance async operations.
"""

import aioredis
from typing import Optional
import logging

class RedisSessionManager:
    def __init__(self, redis_url: str, decode_responses: bool = True):
        self.redis_url = redis_url
        self.decode_responses = decode_responses
        self.redis: Optional[aioredis.Redis] = None
        self.logger = logging.getLogger("RedisSessionManager")

    async def __aenter__(self) -> aioredis.Redis:
        try:
            self.redis = await aioredis.from_url(
                self.redis_url,
                decode_responses=self.decode_responses
            )
            return self.redis
        except Exception as exc:
            self.logger.error(f"Failed to connect to Redis: {exc}")
            raise

    async def __aexit__(self, exc_type, exc, tb):
        if self.redis:
            try:
                await self.redis.close()
            except Exception as exc:
                self.logger.warning(f"Error closing Redis connection: {exc}")

    async def get_client(self) -> aioredis.Redis:
        """
        Returns a connected Redis client (for dependency injection or direct use).
        """
        if not self.redis:
            self.redis = await aioredis.from_url(
                self.redis_url,
                decode_responses=self.decode_responses
            )
        return self.redis
