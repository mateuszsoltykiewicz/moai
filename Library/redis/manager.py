"""
RedisManager: Async, centralized Redis adapter for microservices.

- Provides async methods for KV, hash, pub/sub, streams, locks, and health checks
- Integrates with metrics, centralized logging, and FastAPI lifecycle
- Secure, observable, and extensible
"""

import asyncio
from redis.asyncio import Redis, from_url
from typing import Optional, Any, Dict, AsyncGenerator
from .metrics import record_redis_operation
from .exceptions import RedisConnectionError, RedisOperationError
from Library.logging import get_logger

logger = get_logger(__name__)

class RedisManager:
    def __init__(self, redis_url: str, password: Optional[str] = None, ssl: bool = False):
        self._redis_url = redis_url
        self._password = password
        self._ssl = ssl
        self._client: Optional[Redis] = None

    async def setup(self):
        try:
            self._client = from_url(
                self._redis_url,
                password=self._password,
                ssl=self._ssl,
                encoding='utf-8',
                decode_responses=True,
                health_check_interval=30,
                retry_on_timeout=True,
            )
            pong = await self._client.ping()
            if not pong:
                raise RedisConnectionError("Failed to connect to Redis")
            logger.info("Connected to Redis")
            record_redis_operation("connect")
        except Exception as e:
            logger.error(f"Redis setup failed: {e}", exc_info=True)
            raise RedisConnectionError(str(e))

    async def shutdown(self):
        if self._client:
            await self._client.close()
            logger.info("Redis connection closed")

    # ---- Basic KV Operations ----
    async def get(self, key: str) -> Optional[str]:
        try:
            value = await self._client.get(key)
            record_redis_operation("get")
            return value
        except Exception as e:
            logger.error(f"Redis get failed: {e}", exc_info=True)
            record_redis_operation("get", status="error")
            raise RedisOperationError(str(e))

    async def set(self, key: str, value: str, expire: int = None):
        try:
            await self._client.set(key, value, ex=expire)
            record_redis_operation("set")
        except Exception as e:
            logger.error(f"Redis set failed: {e}", exc_info=True)
            record_redis_operation("set", status="error")
            raise RedisOperationError(str(e))

    async def delete(self, key: str):
        try:
            await self._client.delete(key)
            record_redis_operation("delete")
        except Exception as e:
            logger.error(f"Redis delete failed: {e}", exc_info=True)
            record_redis_operation("delete", status="error")
            raise RedisOperationError(str(e))

    # ---- Hash Operations ----
    async def hgetall(self, key: str) -> Dict[str, Any]:
        try:
            result = await self._client.hgetall(key)
            record_redis_operation("hgetall")
            return result
        except Exception as e:
            logger.error(f"Redis hgetall failed: {e}", exc_info=True)
            record_redis_operation("hgetall", status="error")
            raise RedisOperationError(str(e))

    async def hset(self, key: str, mapping: Dict[str, Any]):
        try:
            await self._client.hset(key, mapping=mapping)
            record_redis_operation("hset")
        except Exception as e:
            logger.error(f"Redis hset failed: {e}", exc_info=True)
            record_redis_operation("hset", status="error")
            raise RedisOperationError(str(e))

    # ---- Pub/Sub ----
    async def publish(self, channel: str, message: str):
        try:
            await self._client.publish(channel, message)
            record_redis_operation("publish")
        except Exception as e:
            logger.error(f"Redis publish failed: {e}", exc_info=True)
            record_redis_operation("publish", status="error")
            raise RedisOperationError(str(e))

    async def subscribe(self, channel: str) -> Any:
        pubsub = self._client.pubsub()
        await pubsub.subscribe(channel)
        return pubsub

    async def listen(self, pubsub) -> AsyncGenerator[Dict[str, Any], None]:
        async for message in pubsub.listen():
            if message['type'] == 'message':
                yield {"channel": message['channel'], "data": message['data']}

    # ---- Distributed Lock ----
    async def acquire_lock(self, name: str, timeout: int = 10) -> Any:
        lock = self._client.lock(name, timeout=timeout)
        await lock.acquire()
        return lock

    async def release_lock(self, lock: Any):
        await lock.release()

    # ---- Stream Operations ----
    async def xadd(self, stream: str, fields: Dict[str, Any], maxlen: int = 1000):
        await self._client.xadd(stream, fields, maxlen=maxlen)
        record_redis_operation("xadd")

    async def xread(self, streams: Dict[str, str], count: int = 10, block: int = 1000):
        return await self._client.xread(streams=streams, count=count, block=block)

    # ---- Health Check ----
    async def health_check(self) -> bool:
        try:
            pong = await self._client.ping()
            return pong is True
        except Exception as e:
            logger.error(f"Redis health check failed: {e}", exc_info=True)
            return False
