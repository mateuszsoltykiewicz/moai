import aioredis
from core.config import AsyncConfigManager

_redis = None

async def get_redis():
    global _redis
    if _redis is None:
        config = await AsyncConfigManager.get()
        _redis = await aioredis.create_redis_pool(config.redis.url)
    return _redis
